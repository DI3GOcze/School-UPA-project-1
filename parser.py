from datetime import datetime
import xml.etree.ElementTree as ET
import zipfile
import os
from urllib import request
from models import link as link_models, station as station_models
from database import Database


class Parser:
    def __init__(self, db: Database, timetable: str = "GVD2022"):
        self.db = db
        self.timetable = timetable

    def __download(self):
        if not os.path.isdir(self.timetable):
            url = f"https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/{self.timetable}.zip"
            request.urlretrieve(url, f"{self.timetable}.zip")

            with zipfile.ZipFile(f"{self.timetable}.zip","r") as zip_ref:
                zip_ref.extractall(self.timetable)

    def __parse_stations(self, stations):
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
            parsed_stations.append(link_models.linkStationStructure(
                id=station.find("./Location/LocationPrimaryCode").text,
                arrivalTime=(
                    station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALA']/Time").text 
                    if station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALA']/Time")
                    else None
                ),
                departureTime=(
                    station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALD']/Time").text
                    if station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALA']/Time")
                    else None
                ),
                trainActivities=train_activities
                ) 
            )
        return parsed_stations

    def parse(self):
        self.__download()
        
        for file in os.listdir(self.timetable):
            print(file)
            file_path = os.path.join(self.timetable, file)
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

            self.db.linkModel.insert(id=link_id, stations=parsed_stations, calendar=[datetime.now()])
