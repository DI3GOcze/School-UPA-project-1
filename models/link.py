from datetime import datetime
from typing import Any
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
    type: Any
    asocTrainID: int

@dataclass
# Data structure for relation between link and station 
class linkStationStructure:
    id: Any
    arrivalTime: datetime
    departureTime: datetime
    trainActivites: list[trainActivityStructure]


class LinkModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        
    def insert(self, id, stations: list[linkStationStructure], calendar: list[datetime]):
        # Create array from linkStationStructure objects
        stationArray = [{
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
            'stations': stationArray,
            'plannedCalendar': calendar 
        })

    def findLinks(self, fromName: str, toName: str, date: datetime)-> list :
        lowerDateLimit = date.replace(hour=0, minute=0, second=0, microsecond=0)
        upperDateLimit = date.replace(hour=23, minute=59, second=59, microsecond=999)

        linkCollection = self.db['link']
        stationCollection = self.db['station']

        stationFrom = stationCollection.find_one({'name': fromName})
        stationTo = stationCollection.find_one({'name': toName})

        if stationFrom == None or stationTo == None or not 'linkIds' in stationFrom or not 'linkIds' in stationTo:
            return []

        possibleLinkIds = list(set(stationFrom['linkIds']) & set(stationTo['linkIds']))     
        


        links = list(linkCollection.aggregate( [
            # Decrese number of possible links
            {
                '$match': { '_id': { '$in' : possibleLinkIds } }
            },
            {
                '$addFields': { 
                    'startingStation': { 
                        '$first': {
                            '$filter': {
                                'input': '$stations',
                                'as': 'station',
                                'cond' : {
                                    '$eq': ['$$station._id', stationFrom['_id'] ]
                                }
                            }
                        } 
                    },
                    'destinationStation': { 
                        '$first': {
                            '$filter': {
                                'input': '$stations',
                                'as': 'station',
                                'cond' : {
                                    '$eq': ['$$station._id', stationTo['_id'] ]
                                }
                            } 
                        }
                    } 
                }
            },
            {
                '$match': { 
                   '$expr': {
                        '$lt': ["$startingStation.arrivalTime", '$destinationStation.arrivalTime']
                    },
                    'plannedCalendar': { '$elemMatch': {'$lt': upperDateLimit, '$gte': lowerDateLimit} } 
                }
            }
            
        ]
        ))

        return links




