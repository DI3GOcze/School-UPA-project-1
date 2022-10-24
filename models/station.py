from dataclasses import dataclass
from pymongo import database

from models.link import linkStationStructure

# Structure :

#   station : {
#       _id :               ID,
#       name:               name,
#       countryCode:        countryCode,
#       locationSubCode:    int,
#       allocationCompany:  int,
#       linkIds:            [
#           linkID: ID
#       ]
#   }

@dataclass
class StationStructure(linkStationStructure):
    name: str
    countryCode: str

class StationModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        self.linkCollection = self.db['link']
        self.stationCollection = self.db['station']
        
    def insert(self, name: str, id: str, countryCode: str):
        # Create array of objects 

        realatedLinks = self.linkCollection.distinct('_id', {
            'stations': { '$elemMatch': {'_id': id} }
        })

        realatedLinks = list(realatedLinks)
        
        self.stationCollection.replace_one({'_id': id}, {
            '_id': id,
            'name': name,
            'countryCode' : countryCode,
            'linkIds': realatedLinks
        }, upsert = True)
