from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import zipfile
import os
from urllib import request
from models import link as link_models, station as station_models
from database import Database


class Parser:
    station_time_format = '%H:%M:%S.0000000%z'
    calendar_datetime_format = '%Y-%m-%dT%H:%M:%S'
    
    def __init__(self, db: Database, timetable: str = "GVD2022"):
        self.db = db
        self.timetable = timetable
        self.__xml_dir = f"temp/{timetable}"

    def __download(self):
        if not os.path.isdir('temp/'):
            os.makedirs('temp/')

        if not os.path.isdir(self.__xml_dir):
            url = f"https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/{self.timetable}.zip"
            request.urlretrieve(url, f"{self.__xml_dir}.zip")

            with zipfile.ZipFile(f"{self.__xml_dir}.zip","r") as zip_ref:
                zip_ref.extractall(self.__xml_dir)

    def __parse_stations(self, stations: list[ET.Element]) -> list[link_models.linkStationStructure]:
        parsed_stations = []
        for station in stations:
            train_activities = [link_models.trainActivityStructure(
                type=activity.find("./TrainActivityType").text,
                asocTrainID=(
                    ET.tostring(activity.find("./AssociatedAttachedTrainID"), encoding='utf-8') 
                    if activity.find("./AssociatedAttachedTrainID") 
                    else None
                ),
                asocOTN=(
                    ET.tostring(activity.find("./AssociatedAttachedOTN"), encoding='utf-8') 
                    if activity.find("./AssociatedAttachedOTN") 
                    else None
                )
            ) for activity in station.findall("./TrainActivity")]

            location_id = station.find("./Location/LocationPrimaryCode")
            location_id = location_id.text if location_id != None else None

            arrival_time = station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALA']/Time")
            arrival_time = datetime.strptime(arrival_time.text, self.station_time_format) if arrival_time != None and arrival_time.text != None else None
            
            departure_time = station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALD']/Time")
            departure_time = datetime.strptime(departure_time.text, self.station_time_format) if departure_time != None and departure_time.text != None else None

            parsed_stations.append(link_models.linkStationStructure(location_id, arrival_time, departure_time, train_activities))
            
        return parsed_stations

    def __parse_calendar(self, calendar: ET.Element) -> list[datetime]:
        parsed_calendar = []
        bitmap_days = calendar.find("./BitmapDays").text
        start_date = datetime.strptime(calendar.find("./ValidityPeriod/StartDateTime").text, self.calendar_datetime_format)
        end_date = datetime.strptime(calendar.find("./ValidityPeriod/EndDateTime").text, self.calendar_datetime_format)

        day_offset = 0
        for day in bitmap_days:
            if day == "1":
                parsed_calendar.append(start_date+timedelta(days=day_offset))
            day_offset+=1
        return parsed_calendar

    def parse(self):
        self.__download()
        
        for file in os.listdir(self.__xml_dir):
            print(file)
            file_path = os.path.join(self.__xml_dir, file)
            tree = ET.parse(file_path)
            root = tree.getroot()

            pa_identifier = root.find("./Identifiers/PlannedTransportIdentifiers/[ObjectType='PA']")
            tr_identifier = root.find("./Identifiers/PlannedTransportIdentifiers/[ObjectType='TR']")
            path_info = root.find("./CZPTTInformation")
            stations = path_info.findall("./CZPTTLocation")
            calendar = path_info.find("./PlannedCalendar")

            pa_id = "_".join(element.text for element in pa_identifier)
            tr_id = "_".join(element.text for element in tr_identifier)
            link_id = pa_id + "__" + tr_id
            
            parsed_stations = self.__parse_stations(stations)
            parsed_calendar = self.__parse_calendar(calendar)

            self.db.linkModel.insert(id=link_id, stations=parsed_stations, calendar=parsed_calendar)
