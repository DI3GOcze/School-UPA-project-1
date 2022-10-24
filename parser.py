from datetime import datetime
import xml.etree.ElementTree as ET
import zipfile
import os
from urllib import request
from models import link as link_models, station as station_models
from database import Database


class Parser:
    timeFormat = '%H:%M:%S.0000000%z'
    
    def __init__(self, db: Database, timetable: str = "GVD2022"):
        self.db = db
        self.timetable = timetable
        self.__xmlDIR = f"temp/{timetable}"

    def __download(self):
        if not os.path.isdir('temp/'):
            os.makedirs('temp/')

        if not os.path.isdir(self.__xmlDIR):
            url = f"https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/{self.timetable}.zip"
            request.urlretrieve(url, f"{self.__xmlDIR}.zip")

            with zipfile.ZipFile(f"{self.__xmlDIR}.zip","r") as zip_ref:
                zip_ref.extractall(self.__xmlDIR)

    def __parse_stations(self, stations: list[ET.Element]):
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

            locationId = station.find("./Location/LocationPrimaryCode")
            locationId = locationId.text if locationId != None else None

            arrivalTime = station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALA']/Time")
            arrivalTime = datetime.strptime(arrivalTime.text, self.timeFormat) if arrivalTime != None and arrivalTime.text != None else None
            
            departureTime = station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALD']/Time")
            departureTime = datetime.strptime(departureTime.text, self.timeFormat) if departureTime != None and departureTime.text != None else None

            parsed_stations.append(link_models.linkStationStructure(locationId, arrivalTime, departureTime, train_activities))
            
        return parsed_stations

    def parse(self):
        self.__download()
        
        for file in os.listdir(self.__xmlDIR):
            print(file)
            file_path = os.path.join(self.__xmlDIR, file)
            tree = ET.parse(file_path)
            root = tree.getroot()

            pa_identifier = root.find("./Identifiers/PlannedTransportIdentifiers/[ObjectType='PA']")
            tr_identifier = root.find("./Identifiers/PlannedTransportIdentifiers/[ObjectType='TR']")
            path_info = root.find("./CZPTTInformation")
            stations = path_info.findall("./CZPTTLocation")
            calendar = path_info.findall("./PlannedCalendar")

            pa_id = "_".join(element.text for element in pa_identifier)
            tr_id = "_".join(element.text for element in tr_identifier)
            link_id = pa_id + "__" + tr_id
            
            parsed_stations = self.__parse_stations(stations)

            self.db.linkModel.insert(id=link_id, stations = parsed_stations, calendar=[datetime.now()])
