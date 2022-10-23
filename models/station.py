from pymongo import database

# Structure :

#   station : {
#       _id :           ID,
#       locationId:     ID,
#       links:          [
#           transportID:    ID
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
#
#       ]

#   }

class StationModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        
    def insert(self, name, id, countryCode):
        collection = self.db['station']
        collection.insert_one({
            
        })
