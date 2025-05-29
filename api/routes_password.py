from flask import Blueprint, request, jsonify
from flasgger.utils import swag_from
from db.user_dao import UserDAO
import bcrypt
import jwt
from dotenv import load_dotenv
load_dotenv()
import os
import datetime
from src.utils.send_email import send_email

password_bp = Blueprint('password', __name__)
user_dao = UserDAO()
SECRET_KEY = os.getenv('SECRET_KEY')
FRONTEND_URL = os.getenv('FRONTEND_URL')

@password_bp.route('password/change_password', methods=['POST'])
@swag_from("docs/change_password.yml")
def change_password():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Authorization header missing or invalid'}), 401

    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_email = decoded.get("email")
        if not user_email:
            return jsonify({'error': 'Token missing email'}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    old_password = data.get("oldPassword")
    new_password = data.get("newPassword")

    if not old_password or not new_password:
        return jsonify({"error": "Old and new password are required."}), 400

    # Fetch user from DB
    user = user_dao.get_user_by_email(user_email)

    # Verify old password
    if not user_dao.verify_password(user.get("email"), old_password):
        return jsonify({"error": "Old password is incorrect."}), 401

    # Hash and update new password
    new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user_dao.collection.update_one({"email": user["email"]}, {"$set": {"password": new_hashed_password}})

    return jsonify({"message": "Password updated successfully."}), 200

@password_bp.route("password/send_reset_email", methods=["POST"])
@swag_from("docs/send_reset_email.yml")
def send_reset_email():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = user_dao.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    userName = user.get("name", "there")

    # Create reset token valid for 30 minutes
    token_payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

    # Construct reset URL
    reset_url = f"{FRONTEND_URL}/reset-password?token={token}"

    subject = "ScoreIt.AI - Reset your password"
    html = f"""
        <h2>Password Reset Request</h2>
        <p>Hi {userName}.Click the button below to reset your password:</p>
        <a href="{reset_url}" style="padding:10px 20px; background:#007bff; color:white; text-decoration:none;">Reset Password</a>
        <p>This link will expire in 30 minutes. If you didn't request this, ignore this email.</p>
    """

    try:
        send_email(email, subject, html)
        return jsonify({"message": "Reset password link sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@password_bp.route("/password/reset_password", methods=["POST"])
@swag_from("docs/reset_password.yml")
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("newPassword")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded.get("email")
        if not email:
            return jsonify({"error": "Token missing email"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    user = user_dao.get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user_dao.collection.update_one({"email": email}, {"$set": {"password": hashed_pw}})

    return jsonify({"message": "Password reset successful."}), 200