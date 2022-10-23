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
        
    def insert(self, name, id, countryCode):
        collection = self.db['station']
        collection.insert_one({
            
        })
