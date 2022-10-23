import config # Tenhle soubor si vytvorte z config_example.py
from pymongo import MongoClient
from models import *

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