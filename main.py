from pymongo import MongoClient
import config # Tenhle soubor si vytvorte z config_example.py
from models import *

class Database():
    def __init__(self) -> None:
        self.get_database()
        self.locationModel = location.LocationModel(self.db)

    def get_database(self):
        # Get connecion
        client = MongoClient(config.CONNECTION_STRING)
        # Get db
        self.db = client[config.DB_NAME]


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   

    database = Database()

    database.locationModel.insert('Siroky Dul', 123452, 'CZ')