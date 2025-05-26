from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
from db.sessions_dao import SessionDAO
import os
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

sessions_bp = Blueprint("sessions", __name__)
session_dao = SessionDAO()

@sessions_bp.route("/session/create", methods=["POST"])
@swag_from("docs/session_create.yml")
def create_session():
    data = request.get_json()
    email = data.get("email")
    token = data.get("token")

    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    session_dao.create_session(email, token)
    return jsonify({"message": "Session created"}), 201

@sessions_bp.route("/session/delete", methods=["POST"])
@swag_from("docs/session_delete.yml")
def delete_session():
    data = request.get_json()
    email = data.get("email")
    token = data.get("token")

    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    session_dao.delete_session(email, token)
    return jsonify({"message": "Session deleted"}), 200

@sessions_bp.route("/session/delete_all", methods=["POST"])
@swag_from("docs/session_delete_all.yml")
def delete_all_sessions():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    session_dao.delete_all_sessions(email)
    return jsonify({"message": "All sessions deleted"}), 200

@sessions_bp.route("/session/check", methods=["POST"])
@swag_from("docs/session_check.yml")
def check_session():
    data = request.get_json()
    email = data.get("email")
    token = data.get("token")

    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    active = session_dao.is_session_active(email, token)
    if not active:
        return jsonify({"active": False}), 200
    
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError:
        session_dao.delete_session(email, token)
        return jsonify({"active": False}), 200
    except InvalidTokenError:
        return jsonify({"active": False}), 200
    except Exception as e:
        return jsonify({"active": False}), 200
    return jsonify({"active": True}), 200

@sessions_bp.route("/session/logout_all", methods=["POST"])
@swag_from("docs/session_logout_all.yml")
def logout_all_devices():
    data = request.get_json()
    email = data.get("email")
    token = data.get("token")

    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    # Delete all sessions
    session_dao.delete_all_sessions(email)

    return jsonify({"message": "Logged out from all devices"}), 200
