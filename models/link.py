from pymongo import database
from dataclasses import dataclass

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

@dataclass
class trainActivityStructure:
    type: int
    asocTrainID: int

@dataclass
# Data structure for relation between link and station 
class linkStationStructure:
    id: any
    arrivalTime: int
    departureTime: int
    trainActivites: list[trainActivityStructure]


class LinkModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        
    def insert(self, id, stations: list[linkStationStructure], calendar: list[int]):
        # Create array from linkStationStructure objects
        linkIdsArray = [{
            '_id': x.id,
            'arrivalTime': x.arrivalTime,
            'departureTime': x.departureTime,
            'trainActivites': [{
                'type': y.type,
                'asocTrainID': y.asocTrainID
                }  for y in x.trainActivites]
            } for x in stations]
        
        linkCollection = self.db['link']
        linkCollection.insert_one({
            '_id': id,
            'linkIds': linkIdsArray,
            'plannedCalendar': calendar 
        })

    def findLinks(self, fromName: str, toName: str, date):
        linksCollection = self.db['link']
