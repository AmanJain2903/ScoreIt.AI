from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
from db.profile_dao import ProfileDAO

MONGO_URI = os.getenv("MONGO_URI")
MONGO_URI_PROD = os.getenv("MONGO_URI_PROD")
DB_NAME = os.getenv("MONGO_DB_NAME")

devClient = MongoClient(MONGO_URI)
dev_db = devClient[DB_NAME]

prodClient = MongoClient(MONGO_URI_PROD)
prod_db = prodClient[DB_NAME]


# UPDATE COLLECTIONS FUNCTIONS
def addToCollection(collection, fields_to_add):
    collection.update_many(
        {},
        {"$set": fields_to_add},
    )
def deleteFromCollection(collection, fields_to_remove):
    collection.update_many(
        {},
        {"$unset": fields_to_remove},
    )

def addNewCollection(collection, fields_to_add):
    collection.insert_one(fields_to_add)

# UPDATE COLLECTIONS

dev_profile_collection = dev_db["profiles"]
prod_profile_collection = prod_db["profiles"]
dev_users_collection = dev_db["users"]
prod_users_collection = prod_db["users"]

# addNewCollection(dev_profile_collection, userProfile)
# addNewCollection(prod_profile_collection, userProfile)
# dao = ProfileDAO()
# dao.collection = prod_profile_collection

# for user in prod_users_collection.find():
#     email = user["email"]
#     print(email)
#     dao.create_profile(email)







        









