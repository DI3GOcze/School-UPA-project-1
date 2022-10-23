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
        
    def insert(self, name: str, id: int, countryCode: str, linkIds: list[int]):
        # Create array of objects 
        sationCollection = self.db['station']
        sationCollection.insert_one({
            '_id': id,
            'name': name,
            'countryCode' : countryCode,
            'linkIds': linkIds
        })
