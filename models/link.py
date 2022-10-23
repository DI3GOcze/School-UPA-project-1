from pymongo import database

# Structure :

#   station : {
#       _id :           ID,
#       locationId:     ID,
#       links:          [
#           _id:                    ID,
#           trainType:              int,
#           trafficType:            int,
#           commercialTrafficType:  int,
#           operationalTrainNumber: int,
#           
#           palannedCalendar:        [
#               date:   Date
#           ]
#       ]
#   }

class StationModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        
    def insert(self, name, id, countryCode):
        collection = self.db['station']
        collection.insert_one({
            
        })
