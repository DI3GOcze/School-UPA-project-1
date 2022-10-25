import sys
from database import Database
from datetime import datetime
from parser import Parser
from models import *

def printLinks(links: list):
    """
    Prints link objects in correct format
    """    
    for link in links:
            print(link['_id'])
            for station in link['stations']:
                for activity in station['trainActivites']:
                    if activity['type'] == '0001':
                        print(f"\t{station['name']}: {station['arrivalTime'].time() if station['arrivalTime'] else 'start'} - {station['departureTime'].time() if station['departureTime'] else 'end'}")
                        break
                
            
            print()

if __name__ == "__main__":   
    database = Database()
    parser = Parser(database)
    argv = sys.argv[1:]

    if len(argv) < 1:
        exit(-1)

    # Parse base import 
    if argv[0] == '--parse-base' and len(argv) == 1:
        parser.parse_base('GVD2022')
    
    # Parse base import and than all months
    elif argv[0] == '--parse-all' and len(argv) == 1:
        parser.parse_all()
    
    # Parse concrete month
    elif argv[0] == '--parse-month' and len(argv) == 2:
        parser.parse_month(argv[1])

    # Search for link
    elif argv[0] == '--search' and len(argv) == 4:
        print(argv[3])
        date = datetime.strptime(argv[3], '%Y-%m-%d')
        links = database.linkModel.findLinks(str(argv[1]), str(argv[2]), date)
        printLinks(links)

    else:
        exit (-1)
        