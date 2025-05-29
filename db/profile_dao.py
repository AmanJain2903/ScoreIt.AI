import bcrypt
from datetime import datetime
from bson.objectid import ObjectId
from db.mongo_connector import profile_collection

class ProfileDAO:
    def __init__(self):
        self.collection = profile_collection

    def create_profile(self, email):
        if self.collection.find_one({"email": email}):
            raise Exception("Profile already exists")

        userProfile = {
            "email": email,
            "resume_text": None,
            "resume_pdf_bytes": None,
            "dark_mode": False,
            "model_preference": 1,
        }

        result = self.collection.insert_one(userProfile)
        return str(result.inserted_id)

    def get_user_profile_by_email(self, email):
        return self.collection.find_one({"email": email})

    def delete_user_profile(self, email):
        result = self.collection.delete_one({"email": email})
        return result.deleted_count == 1

    def update_user_profile(self, email, update_data):
        result = self.collection.update_one({"email": email}, {"$set": update_data})
        return result.modified_count == 1