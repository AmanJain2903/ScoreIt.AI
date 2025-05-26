from flask import Blueprint, request, jsonify, render_template_string
from flasgger.utils import swag_from
import os
import regex as re
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
import datetime
from db.user_dao import UserDAO
from dotenv import load_dotenv
load_dotenv()
import gc
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from src.utils.send_email import send_email

CLIENT_ID = os.getenv("REACT_APP_GOOGLE_CLIENT_ID")

SECRET_KEY = os.getenv("SECRET_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")

auth_bp = Blueprint("auth", __name__)
user_dao = UserDAO()

@auth_bp.route('/google', methods=['POST'])
@swag_from("docs/google.yml")
def google_login():
    try:
        data = request.get_json()
        token = data.get('access_token')

        if not token:
            return jsonify({'error': 'Missing token'}), 400

        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(user_info_url, headers=headers)

        # Extract info
        id_info = response.json()
        email = id_info.get('email')
        name = id_info.get('name')

        if not email:
            return jsonify({'error': 'Invalid token payload'}), 400
        

        user = user_dao.get_user_by_email(email)
        if not user:
            user_dao.create_user(name, email, "", True)
            user = user_dao.get_user_by_email(email)
        else:
            if not user.get("is_google_user"):
                return jsonify({'error': 'User already registered. Login with Password instead.'}), 400
        
        # ✅ Generate JWT token
        payload = {
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({
            'token': token,
            'name': user['name'],
            'email': user['email'],
            "is_google_user" : True, 
            "dark_mode" : user.get("dark_mode")
        }), 200

    except ValueError as e:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
        if user_dao.get_user_by_email(email).get("is_google_user"):
            return jsonify({"error": "Email already registered. Login with Google instead."}), 409
        else:
            return jsonify({"error": "Email already registered"}), 409

    user_dao.create_user(name, email, password, False)
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
    
    if user.get("is_google_user"):
        return jsonify({"error": "Login with Google instead."}), 409
    
    if not user.get("verified"):
        return jsonify({"error": "Please verify your email to login"}), 401

    if not user_dao.verify_password(email, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ Generate JWT token
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    name = user.get("name", "")

    try:
        del data
        del password
    except Exception:
        pass
    gc.collect()

    return jsonify({"token": token, "name" : name, "email" : email, "is_google_user" : False, "dark_mode" : user.get("dark_mode")}), 200

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
    
    if user.get("is_google_user"):
        try:
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {"Authorization": f"Bearer {password}"}
            response = requests.get(user_info_url, headers=headers)

            # Extract info
            id_info = response.json()
            email = id_info.get('email')
            
            if id_info.get("email") != email:
                return jsonify({"error": "Invalid credentials"}), 401
        except Exception as e:
            return jsonify({"error": "Invalid credentials"}), 401
    else:
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

@auth_bp.route("/update", methods=["POST"])
@swag_from("docs/update.yml")
def update():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400
    user = user_dao.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    collection = user_dao.collection
    
    collection.update_one({"email": email}, {"$set": {"dark_mode": not user.get("dark_mode")}})

    return jsonify({"message": "User updated successfully"}), 200
    
@auth_bp.route("/send_email", methods=["POST"])
@swag_from("docs/send_email.yml")
def send_verification_email():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = user_dao.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Create token for email verification valid for 30 minutes
    token_payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")
    
    # Construct verification URL
    verify_url = f"{FRONTEND_URL}/verify?token={token}"

    subject = "ScoreIt.AI - Verify your email address"
    html = f"""
        <h2>Welcome to ScoreIt.AI!</h2>
        <p>Click below to verify your email address:</p>
        <a href="{verify_url}" style="padding:10px 20px; background:#007bff; color:white; text-decoration:none;">Verify Email</a>
        <p>This link will expire in 30 minutes.</p>
    """

    try:
        send_email(email, subject, html)
        return jsonify({"message": "Verification email sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route("/verify_email", methods=["GET"])
@swag_from("docs/verify_email.yml")
def verify_email():
    token = request.args.get("token")
    
    if not token:
        return render_template_string("<h2>Invalid verification link.</h2>"), 400

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")

        if not email:
            return render_template_string("<h2>Invalid token payload.</h2>"), 400

        user = user_dao.get_user_by_email(email)
        if not user:
            return render_template_string("<h2>User not found.</h2>"), 404

        if user.get("verified"):
            return render_template_string("<h2>Your email is already verified.</h2>"), 200

        # Update user document
        user_dao.collection.update_one(
            {"email": email},
            {"$set": {"verified": True}}
        )
        return render_template_string("<h2>Your email has been successfully verified. You can now log in to ScoreIt.AI.</h2>"), 200

    except ExpiredSignatureError:
        return render_template_string("<h2>Verification link has expired.</h2>"), 400
    except InvalidTokenError:
        return render_template_string("<h2>Invalid verification token.</h2>"), 400
    except Exception as e:
        return render_template_string(f"<h2>Error: {str(e)}</h2>"), 500