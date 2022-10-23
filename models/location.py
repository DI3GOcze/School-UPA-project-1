from pymongo import database

#   Structure :
#   location : {
#       _id :           ID,
#       name:           name,
#       countryCode:    countryCode
#   }

class LocationModel:
    
    def __init__(self, db : database.Database):
        self.db = db
        
    def insert(self, name, id, countryCode):
        collection = self.db['location']
        collection.insert_one({
            '_id':  id,
            'name': name,
            'countryCode': countryCode
        })
