from pymongo import database

# Structure :

#   link : {
#       _id:                    ID,
#       trainType:              int,
#       trafficType:            int,
#       commercialTrafficType:  int,
#       operationalTrainNumber: int,
#           
#       stations:   [
#           _id:            ID
#           arrivalTime:    Time,
#           departureTime:  Time,
#           responsibleRU:  ID,
#           responsibleIM:  ID,
#           trainActivites: [
#               type:           int,
#               asocTrainID:    ID,               
#           ]
#           
#           networkSpecificParams:  [
#               name:   string
#               value:  any
#           ]           
#       ]
#
#        plannedCalendar:   [
#           date:   Date
#        ]
#   }

class LinkModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        
    def insert(self, name, id, countryCode):
        collection = self.db['link']
        collection.insert_one({
            
        })
