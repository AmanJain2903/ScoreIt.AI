from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
import os
import regex as re
import jwt
import datetime
from db.user_dao import UserDAO
from dotenv import load_dotenv
load_dotenv()
import gc

SECRET_KEY = os.getenv("SECRET_KEY")

auth_bp = Blueprint("auth", __name__)
user_dao = UserDAO()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@auth_bp.route("/register", methods=["POST"])
@swag_from("docs/register.yml")
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 553

    if user_dao.get_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409

    user_dao.create_user(name, email, password)
    try:
        del data
        del email
        del password
        del name
    except Exception:
        pass
    gc.collect()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
@swag_from("docs/login.yml")
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = user_dao.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user_dao.verify_password(email, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Generate JWT token
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    name = user.get("name", "")

    try:
        del data
        del password
    except Exception:
        pass
    gc.collect()

    return jsonify({"token": token, "name" : name, "email" : email}), 200

@auth_bp.route("/delete", methods=["POST"])
@swag_from("docs/delete.yml")
def delete():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = user_dao.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user_dao.verify_password(email, password):
        return jsonify({"error": "Invalid credentials"}), 401

    user_dao.delete_user(email)

    try:
        del data
        del email
        del password
        del user
    except Exception:
        pass
    gc.collect()

    return jsonify({"message": "User deleted successfully"}), 200