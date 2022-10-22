from pymongo import MongoClient
import config # Tenhle soubor si vytvorte z config_example.py

def get_database():
 
    # Provide the mongodb atlas url to connect python to mongodb using pymongo

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(config.CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[config.DB_NAME]
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
    # Get the database
    dbname = get_database()

    collection_name = dbname["test"]

    item_1 = {
    "_id" : "1",
    "name" : "test1"
    }

    collection_name.insert_one(item_1)