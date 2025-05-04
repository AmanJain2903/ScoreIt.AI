import bcrypt
from datetime import datetime
from bson.objectid import ObjectId
from db.mongo_connector import users_collection

class UserDAO:
    def __init__(self):
        self.collection = users_collection

    def create_user(self, name, email, password):
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user = {
            "name": name,
            "email": email,
            "password": hashed_pw,
            "verified": False,
            "created_at": datetime.utcnow(),
            "resume_text": None,
            "resume_pdf_bytes": None  # Can store base64 encoded string here later
        }

        result = self.collection.insert_one(user)
        return str(result.inserted_id)

    def get_user_by_email(self, email):
        return self.collection.find_one({"email": email})

    def delete_user(self, email):
        result = self.collection.delete_one({"email": email})
        return result.deleted_count == 1

    def verify_password(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user["password"])