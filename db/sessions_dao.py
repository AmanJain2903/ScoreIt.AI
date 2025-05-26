from db.mongo_connector import sessions_collection
from datetime import datetime

class SessionDAO:
    def __init__(self):
        self.collection = sessions_collection

    def create_session(self, email, token):
        session = {
            "email": email,
            "token": token,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        self.collection.insert_one(session)

    def delete_session(self, email, token):
        self.collection.delete_one(
            {"email": email, "token": token}
        )

    def delete_all_sessions(self, email):
        self.collection.delete_many(
            {"email": email}
        )

    def is_session_active(self, email, token):
        session = self.collection.find_one(
            {"email": email, "token": token, "is_active": True}
        )
        return session is not None

    def get_active_sessions(self, email):
        return list(self.collection.find(
            {"email": email, "is_active": True},
            {"_id": 0, "token": 1, "created_at": 1}
        ))