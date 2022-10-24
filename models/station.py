from pymongo import database

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

class StationModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        self.linkCollection = self.db['link']
        self.stationCollection = self.db['station']
        
    def insert(self, name: str, id: str, countryCode: str, realatedLinks: list):
        self.stationCollection.replace_one({'_id': id}, {
            '_id': id,
            'name': name,
            'countryCode' : countryCode,
            'linkIds': realatedLinks
        }, upsert = True)

    def get(self, id):
        return self.stationCollection.find_one({'_id': id})

    def addRealtionToLink(self, stationId, linkId):
        return self.stationCollection.update_one({'_id': stationId}, {
                '$addToSet': { 'linkIds': linkId } 
            }
        )

    def removeRealtionToLink(self, stationId, linkId):
        return self.stationCollection.update_one({'_id': stationId}, {
                '$pull': { 'linkIds': linkId } 
            }
        )

    def autoUpdateStationRelatedLinks(self, id):
        realatedLinks = self.linkCollection.distinct('_id', {
            'stations': { '$elemMatch': {'_id': id} }
        })

        realatedLinks = list(realatedLinks)

        return self.stationCollection.update_one({'_id': id}, {'linkIds': realatedLinks})
