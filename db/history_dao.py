from bson.objectid import ObjectId
from datetime import datetime
from db.mongo_connector import history_collection

class HistoryDAO:
    def __init__(self):
        self.collection = history_collection

    def save_history(self, user_email: str, resume_text: str, resume_json: dict, jd_text: str, jd_json: dict, match_report: dict):
        history_doc = {
            "user_email": user_email,
            "resume_text": resume_text,
            "resume_json": resume_json,
            "jd_text": jd_text,
            "jd_json": jd_json,
            "match_report": match_report,
            "timestamp": datetime.utcnow()
        }
        result = self.collection.insert_one(history_doc)
        return str(result.inserted_id)

    def get_history(self, user_email: str):
        records = list(self.collection.find({"user_email": user_email}, {"_id": 0}))
        return records
    
    def delete_match_by_id(self, user_email, match_id):
        result = self.collection.delete_one({
            "_id": ObjectId(match_id),
            "user_email": user_email
        })
        return result.deleted_count == 1

    def clear_history(self, user_email: str):
        result = self.collection.delete_many({"user_email": user_email})
        return result.deleted_count