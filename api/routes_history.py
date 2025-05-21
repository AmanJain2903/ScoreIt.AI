from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
import bcrypt
import os
import regex as re
import jwt
import datetime
from db.history_dao import HistoryDAO
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

history_bp = Blueprint("history", __name__)
history_dao = HistoryDAO()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@history_bp.route("/history/add", methods=["POST"])
@swag_from("docs/history_add.yml")
def add_history():
    data = request.get_json()
    email = data.get("email")
    resume_text = data.get("resume_text")
    resume_json = data.get("resume_json")
    jd_text = data.get("jd_text")
    jd_json = data.get("jd_json")
    match_report = data.get("match_report")
    if not email or not resume_text or not resume_json or not jd_text or not jd_json or not match_report:
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    if not isinstance(resume_text, str) or not isinstance(resume_json, dict) or not isinstance(jd_text, str) or not isinstance(jd_json, dict) or not isinstance(match_report, dict):
        return jsonify({"error": "Invalid data types"}), 400
    try:
        history_id = history_dao.save_history(email, resume_text, resume_json, jd_text, jd_json, match_report)
        return jsonify({"message": "History added successfully", "history_id": history_id}), 200
    except Exception:
        return jsonify({"error": "Failed to save history"}), 500
    
@history_bp.route("/history/get_all", methods=["POST"])
@swag_from("docs/history_get_all.yml")
def get_all_history():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    try:
        history = history_dao.get_history(email)
        if not history:
            return jsonify({"message": "No history found"}), 404
        return jsonify({"history": history}), 200
    except Exception:
        return jsonify({"error": "Failed to retrieve history"}), 500

@history_bp.route("/history/delete_one", methods=["DELETE"])
@swag_from("docs/history_delete_one.yml")
def delete_one_history():
    data = request.get_json()
    email = data.get("email")
    match_id = data.get("match_id")
    if not email or not match_id:
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    try:
        deleted = history_dao.delete_match_by_id(email, match_id)
        if deleted:
            return jsonify({"message": "Match report deleted successfully"}), 200
        else:
            return jsonify({"error": "No match report found with the given ID"}), 404
    except Exception:
        return jsonify({"error": "Failed to delete match report"}), 500

@history_bp.route("/history/delete_all", methods=["DELETE"])
@swag_from("docs/history_delete_all.yml")
def delete_all_history():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Missing required fields"}), 400
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    try:
        deleted_count = history_dao.clear_history(email)
        if deleted_count > 0:
            return jsonify({"message": f"Deleted {deleted_count} history records successfully"}), 200
        else:
            return jsonify({"message": "No history records found to delete"}), 200
    except Exception:
        return jsonify({"error": "Failed to delete history records"}), 500