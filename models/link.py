from datetime import datetime
from typing import Any, Optional
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
    asocTrainID: Optional[str]
    asocOTN: Optional[str]

@dataclass
# Data structure for relation between link and station 
class linkStationStructure:
    id: Any
    arrivalTime: Optional[datetime]
    departureTime: Optional[datetime]
    trainActivities: list[trainActivityStructure]


class LinkModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        self.linkCollection = self.db['link']
        self.stationCollection = self.db['station']
        
    def insert(self, id, stations: list[linkStationStructure], calendar: list[datetime]):
        """
        Insert new link entry or update current one
        """
        # Create array from linkStationStructure objects
        stationArray = [{
            '_id': x.id,
            'arrivalTime': x.arrivalTime,
            'departureTime': x.departureTime,
            'trainActivites': [{
                'type': y.type,
                'asocTrainID': y.asocTrainID,
                'asocOTN': y.asocOTN
                }  for y in x.trainActivities]
            } for x in stations]
        
        self.linkCollection.replace_one({'_id': id},
        {
            '_id': id,
            'stations': stationArray,
            'plannedCalendar': calendar 
        }, upsert=True )

    def get(self, id):
        """
        Returns link with given ID
        """
        return self.linkCollection.find_one({'_id': id})

    def deleteFromCalendar(self, id, dates: list):
        """
        Deletes all dates from link kalendark, that were passed in argument
        """
        self.linkCollection.update_one({'_id': id}, {
            '$pull': { 'plannedCalendar': {'$in': dates} } 
        })


    def findLinks(self, fromName: str, toName: str, date: datetime)-> list :
        """
        Finds and returns all links, that correspod with passed arguments
        """
        lowerDateLimit = date.replace(hour=0, minute=0, second=0, microsecond=0)
        upperDateLimit = date.replace(hour=23, minute=59, second=59, microsecond=999)

        stationFrom = self.stationCollection.find_one({'name': fromName})
        stationTo = self.stationCollection.find_one({'name': toName})

        if stationFrom == None or stationTo == None or not 'linkIds' in stationFrom or not 'linkIds' in stationTo:
            return []

        # Possible links are intersection between starting and destination station link lists
        possibleLinkIds = list(set(stationFrom['linkIds']) & set(stationTo['linkIds']))     
        
        links = list(self.linkCollection.aggregate( [
            # Filter by links, that are related to both stations
            {
                '$match': { '_id': { '$in' : possibleLinkIds } }
            },

            # Specify starting station and destination station
            {
                '$addFields': { 
                    'startingStation': { 
                        '$arrayElemAt': [
                            '$stations',
                            { 
                                '$indexOfArray': [
                                    '$stations._id',
                                    stationFrom['_id']
                                ] 
                            }
                        ] 
                    }, 
                    'destinationStation': { 
                        '$arrayElemAt': [
                            '$stations',
                            { 
                                '$indexOfArray': [
                                    '$stations._id',
                                    stationTo['_id']
                                ] 
                            }
                        ] 
                    } 
                }
            },
            {
                '$match': { 
                   # Filter links that have correct order of starting and destination sations
                    'startingStation.departureTime': {'$ne' : None},
                    'destinationStation.arrivalTime': {'$ne' : None},
                    '$expr': {
                        '$lt': ['$startingStation.departureTime', '$destinationStation.arrivalTime']
                    },
                    # Filter stations by date
                    'plannedCalendar': { '$elemMatch': {'$lt': upperDateLimit, '$gte': lowerDateLimit} } 
                }
            },

            # Add station detais (name,...)
            {
                '$lookup': {
                    'from': 'station',
                    'localField': 'stations._id',
                    'foreignField': '_id',
                    'as': 'stationsInfo'
                }
            },
            { 
                '$addFields': {
                    'stations': {
                        '$map': {
                            'input': '$stations',
                            'in': {
                                '$mergeObjects': [
                                    '$$this',
                                    { 
                                        '$arrayElemAt': [
                                            '$stationsInfo',
                                            { 
                                                '$indexOfArray': [
                                                    '$stationsInfo._id',
                                                    '$$this._id'
                                                ] 
                                            }
                                        ] 
                                    }
                                ] 
                            }
                        }
                    }
                } 
            },
            {
                '$sort': {'startingStation.departureTime': 1}
            },
            { '$project': {
                'stations': 1, '_id': 1
            }},
        ]
        ))

        return links
