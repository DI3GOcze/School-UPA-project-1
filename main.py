import config # Tenhle soubor si vytvorte z config_example.py
from models import *
from models.link import linkStationStructure, trainActivityStructure
from datetime import timedelta, datetime
from pymongo import MongoClient


class Database():
    def __init__(self) -> None:
        self.get_database()
        self.linkModel = link.LinkModel(self.db)
        self.stationModel = station.StationModel(self.db)


    def get_database(self):
        # Get connecion
        client = MongoClient(config.CONNECTION_STRING)
        # Get db
        self.db = client[config.DB_NAME]

# Temp function for dummy data
def insertDummyLinks(database: Database):
    
    nowdate = datetime.now()

    stations = [
            linkStationStructure(1, nowdate + timedelta(hours=1), nowdate, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(2, nowdate + timedelta(hours=2), nowdate, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(3, nowdate + timedelta(hours=3), nowdate, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(4, nowdate + timedelta(hours=4), nowdate, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(5, nowdate + timedelta(hours=5), nowdate, [
                trainActivityStructure('001', 1)
            ])
        ]

    # %f nejde pouzit, protoze je to .0000000 prilis dlouhy, takze proste jen skip
    timeFormat = '%H:%M:%S.0000000%z'

    database.linkModel.insert(4, stations, datetime.strptime('18:03:00.0000000+01:00', timeFormat))
 
# Temp function for dummy data
def insertDummyStations(database: Database):
    database.stationModel.insert('Siroky Dul', 7 , 'CZ', [1])
    database.stationModel.insert('Policka', 8 , 'CZ', [1])
    database.stationModel.insert('Bystre', 9 , 'CZ', [1])
    database.stationModel.insert('Brno', 10 , 'CZ', [1])
    database.stationModel.insert('Praha', 11 , 'CZ', [1])


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   

    database = Database()

    insertDummyStations(database)
    insertDummyLinks(database)
