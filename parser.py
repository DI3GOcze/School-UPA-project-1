from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import zipfile
import os
import re
import gzip
import shutil
import zipfile
from retry import retry
from urllib import request, error
from urllib.parse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
from models import link as link_models, station as station_models
from database import Database

_BASE_URL = 'https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/'
_MONTHS = [
    '2021-12',
    '2022-01',
    '2022-02',
    '2022-03',
    '2022-04',
    '2022-05',
    '2022-06',
    '2022-07',
    '2022-08',
    '2022-09',
    '2022-10',
]

class Parser:
    station_time_format = '%H:%M:%S.0000000%z'
    calendar_datetime_format = '%Y-%m-%dT%H:%M:%S'
    
    def __init__(self, db: Database, dir="tmp"):
        self.db = db
        self.dir = dir

    def __download_base(self, filename):
        timetable_dir = os.path.join(self.dir, filename)
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)

        if not os.path.isdir(timetable_dir):
            url = f"https://portal.cisjr.cz/pub/draha/celostatni/szdc/2022/{filename}.zip"
            request.urlretrieve(url, f"{timetable_dir}.zip")

            with zipfile.ZipFile(f"{timetable_dir}.zip","r") as zip_ref:
                zip_ref.extractall(timetable_dir)

    def __ensure_folders_created(self, folder_path):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        
        if not os.path.isdir(folder_path):
            os.path.join(folder_path)

        if not os.path.isdir(f'{folder_path}/downloaded'):
            os.makedirs(f'{folder_path}/downloaded')

        if not os.path.isdir(f'{folder_path}/downloaded'):
            os.makedirs(f'{folder_path}/downloaded')

        if not os.path.isdir(f'{folder_path}/new'):
            os.makedirs(f'{folder_path}/new')

        if not os.path.isdir(f'{folder_path}/cancelled'):
            os.makedirs(f'{folder_path}/cancelled')

        if not os.path.isdir(f'{folder_path}/downloaded/new'):
            os.makedirs(f'{folder_path}/downloaded/new')

        if not os.path.isdir(f'{folder_path}/downloaded/cancelled'):
            os.makedirs(f'{folder_path}/downloaded/cancelled')

    @retry(error.URLError, tries=4, delay=3, backoff=2)
    def __download_file(self, link, folder_path, folderName, fileName):
        print(f'Downloading {fileName}')
        request.urlretrieve(f"https://portal.cisjr.cz/{link['href']}", os.path.join(folder_path, "downloaded", folderName, fileName+".zip"))

    def __download_month(self, folder_name):
        folder_path = os.path.join(self.dir, folder_name)
        self.__ensure_folders_created(folder_path)

        response = request.urlopen(_BASE_URL+folder_name).read().decode('utf-8')

        for link in BeautifulSoup(response, parse_only=SoupStrainer('a', href = re.compile('.*xml|.*xml.zip')), features="html.parser"):
            fileName = os.path.basename(urlparse(link['href']).path).replace('.xml.zip', '')
            folderName = 'cancelled' if re.search("cancel.*", fileName) else 'new'

            if os.path.isfile(os.path.join(folder_path, folderName, fileName+".xml")):
                continue

            try:
                self.__download_file(link, folder_path, folderName, fileName)
            except:
                continue
            
            is_zip = zipfile.is_zipfile(os.path.join(folder_path, "downloaded", folderName, fileName+".zip"))

            if is_zip:
                with zipfile.ZipFile(os.path.join(folder_path, "downloaded", folderName, fileName+".zip"),"r") as zip_ref:
                    zip_ref.extractall(os.path.join(folder_path, folderName))
    
            else:
                with gzip.open(os.path.join(folder_path, "downloaded", folderName, fileName+".zip"), 'rb') as f_in:
                    with open(os.path.join(folder_path, folderName, fileName+".xml"), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
               
    def __parse_stations(self, stations: list[ET.Element]) -> list[station_models.StationStructure]:
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

            
            id = station.find("./Location/LocationPrimaryCode").text
            name = station.find("./Location/PrimaryLocationName").text
            country_code = station.find("./Location/CountryCodeISO").text

            arrival_time = station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALA']/Time")
            arrival_time = (
                datetime.strptime(arrival_time.text, self.station_time_format) 
                if arrival_time != None and arrival_time.text != None 
                else None
            )
            
            departure_time = station.find("./TimingAtLocation/Timing[@TimingQualifierCode='ALD']/Time")
            departure_time = (
                datetime.strptime(departure_time.text, self.station_time_format) 
                if departure_time != None and departure_time.text != None 
                else None
            )

            parsed_stations.append(station_models.StationStructure(
                id=id, arrivalTime=arrival_time, departureTime=departure_time, trainActivities=train_activities, name=name, countryCode=country_code)
            )
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

    def __insert_stations(self, stations: list[station_models.StationStructure], link_id):
        for station in stations:
            isStopping = False
            for activity in station.trainActivities:
                if activity.type == '0001':
                    isStopping = True
                    break
            
            if not isStopping:
                continue

            currentStation = self.db.stationModel.get(station.id)
            if currentStation != None:
                self.db.stationModel.addRealtionToLink(station.id, link_id)
            else:
                self.db.stationModel.insert(name=station.name, id=station.id, countryCode=station.countryCode, realatedLinks = [link_id])

    def __parse_cancelled(self, path):        
        for file in os.listdir(path):
            print(file)
            file_path = os.path.join(path, file)
            tree = ET.parse(file_path)
            root = tree.getroot()

            pa_identifier = root.find("./PlannedTransportIdentifiers/[ObjectType='PA']")
            tr_identifier = root.find("./PlannedTransportIdentifiers/[ObjectType='TR']")
            
            calendar = root.find("./PlannedCalendar")

            pa_id = "_".join(element.text for element in pa_identifier)
            tr_id = "_".join(element.text for element in tr_identifier)
            link_id = pa_id + "__" + tr_id
            
            parsed_calendar = self.__parse_calendar(calendar)

            self.db.linkModel.deleteFromCalendar(link_id, parsed_calendar)

    def __parse(self, path):        
        for file in os.listdir(path):
            print(file)
            file_path = os.path.join(path, file)
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

            self.__insert_stations(parsed_stations, link_id)

            self.db.linkModel.insert(id=link_id, stations=parsed_stations, calendar=parsed_calendar)

    def parse_month(self, folder_name):
        self.__download_month(folder_name)
        path_to_cancelled = os.path.join(self.dir, folder_name, "cancelled")
        path_to_new = os.path.join(self.dir, folder_name, "new")
        self.__parse_cancelled(path_to_cancelled)
        self.__parse(path_to_new)

    def parse_base(self, filename):
        self.__download_base(filename)
        path_to_base = os.path.join(self.dir, filename)
        self.__parse(path_to_base)

    def parse_all(self):
        self.parse_base('GVD2022')
        for month in _MONTHS:
            self.parse_month(month)

