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
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401
    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400
    session_dao.create_session(email, token)
    return jsonify({"message": "Session created"}), 201

@sessions_bp.route("/session/delete", methods=["DELETE"])
@swag_from("docs/session_delete.yml")
def delete_session():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401

    if not email or not token:
        return jsonify({"error": "Email and token are required"}), 400

    session_dao.delete_session(email, token)
    return jsonify({"message": "Session deleted"}), 200

@sessions_bp.route("/session/delete_all", methods=["DELETE"])
@swag_from("docs/session_delete_all.yml")
def delete_all_sessions():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401
    if not email:
        return jsonify({"error": "Email is required"}), 400

    session_dao.delete_all_sessions(email)
    return jsonify({"message": "All sessions deleted"}), 200

@sessions_bp.route("/session/check", methods=["GET"])
@swag_from("docs/session_check.yml")
def check_session():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
    except Exception:
        return jsonify({'error': 'Invalid token'}), 401
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

