from pymongo import database

# Structure :

#   link : {
#           _id:                    ID,
#           trainType:              int,
#           trafficType:            int,
#           commercialTrafficType:  int,
#           operationalTrainNumber: int,
#           
#           plannedCalendar:        [
#              date:   Date
#           ]
#   }

class LinkModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        
    def insert(self, name, id, countryCode):
        collection = self.db['link']
        collection.insert_one({
            
        })
