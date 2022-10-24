from datetime import timedelta, datetime
from models import *
from models.link import linkStationStructure, trainActivityStructure
from parser import Parser
from database import Database

# Temp function for dummy data
def insertDummyLinks(database: Database):
    
    nowdate = datetime.now()

    stations = [
            linkStationStructure(1, nowdate + timedelta(hours=1), nowdate, [
                trainActivityStructure('001', "1", "1")
            ]),
            linkStationStructure(2, nowdate + timedelta(hours=2), nowdate, [
                trainActivityStructure('001', "1", "1")
            ]),
            linkStationStructure(3, nowdate + timedelta(hours=3), nowdate, [
                trainActivityStructure('001', "1", "1")
            ]),
            linkStationStructure(4, nowdate + timedelta(hours=4), nowdate, [
                trainActivityStructure('001', "1", "1")
            ]),
            linkStationStructure(5, nowdate + timedelta(hours=5), nowdate, [
                trainActivityStructure('001', "1", "1")
            ])
        ]

    database.linkModel.insert(1, stations, [nowdate, nowdate + timedelta(days=3)])

 
# Temp function for dummy data
def insertDummyStations(database: Database):
    database.stationModel.insert('Krhanice', '55766' , 'CZ')
    database.stationModel.insert('vl. v km 14,422', '55767' , 'CZ')
    database.stationModel.insert('Prosečnice', '55776' , 'CZ')
    database.stationModel.insert('Kamenný Přívoz', '55756' , 'CZ')
    database.stationModel.insert('Jílové u Prahy', '55736' , 'CZ')


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   

    database = Database()

    # parser = Parser(database)
    # parser.parse()
    # insertDummyStations(database)
    # insertDummyLinks(database)

    result = database.linkModel.findLinks('Krhanice', 'Prosečnice', datetime.now())
    print(result)