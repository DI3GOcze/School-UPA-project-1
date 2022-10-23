from pymongo import MongoClient
import config # Tenhle soubor si vytvorte z config_example.py
from models import *
from models.link import linkStationStructure, trainActivityStructure

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
    stations = [
            linkStationStructure(1, 5, 5, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(2, 6, 6, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(3, 7, 7, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(4, 9, 9, [
                trainActivityStructure('001', 1)
            ]),
            linkStationStructure(5, 10, 10, [
                trainActivityStructure('001', 1)
            ])
        ]

    database.linkModel.insert(4, stations)

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
