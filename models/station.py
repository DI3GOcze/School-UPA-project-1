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
        
    def insert(self, name: str, id: str, countryCode: str, realatedLinks: list = []):
        """
        Insert new station entry or update current one
        """
        self.stationCollection.replace_one({'_id': id}, {
            '_id': id,
            'name': name,
            'countryCode' : countryCode,
            'linkIds': realatedLinks
        }, upsert = True)

    def get(self, id):
        """
        Returns station with given ID
        """
        return self.stationCollection.find_one({'_id': id})

    def addRealtionToLink(self, stationId, linkId):
        """
        Adds id of passed link to stations link relation array
        """
        return self.stationCollection.update_one({'_id': stationId}, {
                '$addToSet': { 'linkIds': linkId } 
            }
        )

    def removeRealtionToLink(self, stationId, linkId):
        """
        Removes id of passed link from stations link relation array
        """
        return self.stationCollection.update_one({'_id': stationId}, {
                '$pull': { 'linkIds': linkId } 
            }
        )

    def autoUpdateStationRelatedLinks(self, id):
        """
        Automatically updates link realtion array 
        """
        realatedLinks = self.linkCollection.distinct('_id', {
            'stations': { '$elemMatch': {'_id': id} }
        })

        realatedLinks = list(realatedLinks)

        return self.stationCollection.update_one({'_id': id}, {'linkIds': realatedLinks})
