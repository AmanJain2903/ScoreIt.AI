from flask import Blueprint, request, jsonify, render_template_string
from flasgger.utils import swag_from
import os
import regex as re
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import datetime
from db.profile_dao import ProfileDAO
from dotenv import load_dotenv
load_dotenv()
import gc
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests

profile_bp = Blueprint('profile', __name__)
dao = ProfileDAO()
SECRET_KEY = os.getenv("SECRET_KEY")



@profile_bp.route('/profile/create', methods=['POST'])
@swag_from("docs/create_profile.yml")
def CreateProfile():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return {"error": "Email is required"}, 400
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return {"error": "Invalid email address"}, 400
    if dao.get_user_profile_by_email(email):
        return {"error": "Profile already exists"}, 400
    try:
        profile_id = dao.create_profile(email)
        return {"message": "Profile created", "id": profile_id}, 201
    except Exception as e:
        return {"error": str(e)}, 400


@profile_bp.route('/profile/read', methods=['GET'])
@swag_from("docs/read_profile.yml")
def ReadProfile():
    header = request.headers.get('Authorization')
    if not header or not header.startswith('Bearer '):
        return {"error": "Authorization header missing or invalid"}, 401
    token = header.split(' ')[1]
    if not token:
        return {"error": "Token is required"}, 401
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
        if not email:
            return {"error": "Email is required"}, 401
    except Exception as e:
        return {"error": str(e)}, 401
    profile = dao.get_user_profile_by_email(email)
    if not profile:
        return {"error": "Profile not found"}, 404
    profile["_id"] = str(profile["_id"])
    return jsonify(profile), 200


@profile_bp.route('/profile/update', methods=['POST'])
@swag_from("docs/update_profile.yml")
def UpdateProfile():
    header = request.headers.get('Authorization')
    if not header or not header.startswith('Bearer '):
        return {"error": "Authorization header missing or invalid"}, 401
    token = header.split(' ')[1]
    if not token:
        return {"error": "Token is required"}, 401
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
        if not email:
            return {"error": "Email is required"}, 401
    except Exception as e:
        return {"error": str(e)}, 401
    data = request.get_json()
    updateData = data.get('update_data')
    if not updateData:
        return {"error": "Update data is required"}, 400
    updated = dao.update_user_profile(email, updateData)
    if updated:
        return {"message": "Profile updated"}, 200
    return {"error": "Profile not found or no change"}, 404


@profile_bp.route('/profile/delete', methods=['DELETE'])
@swag_from("docs/delete_profile.yml")
def DeleteProfile():
    header = request.headers.get('Authorization')
    if not header or not header.startswith('Bearer '):
        return {"error": "Authorization header missing or invalid"}, 401
    token = header.split(' ')[1]
    if not token:
        return {"error": "Token is required"}, 401
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
        if not email:
            return {"error": "Email is required"}, 401
    except Exception as e:
        return {"error": str(e)}, 401
    deleted = dao.delete_user_profile(email)
    if deleted:
        return {"message": "Profile deleted"}, 200
    return {"error": "Profile not found"}, 404