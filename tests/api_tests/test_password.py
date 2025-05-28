import pytest
import json
import bcrypt
import jwt
from api.app import create_app
from db.user_dao import UserDAO
import os
import datetime
from unittest.mock import patch

pytestmark = pytest.mark.api
SECRET_KEY = os.getenv("SECRET_KEY")
user_dao = UserDAO()

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

@pytest.fixture
def mock_user():
    name = "Test User"
    email = "testuser@example.com"
    password = "oldPassword123"
    user_dao.create_user(name, email, password, False)
    yield {"email": email, "password": password}
    user_dao.delete_user(email)

def generate_token(email):
    payload = {
        "email" : email,
        "exp" : datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_successful_password_change(client, mock_user):
    token = generate_token(mock_user["email"])
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "oldPassword": mock_user["password"],
        "newPassword": "newSecret456"
    }

    response = client.post("password/change_password", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "Password updated successfully."

    updated_user = user_dao.get_user_by_email(mock_user["email"])
    assert bcrypt.checkpw("newSecret456".encode(), updated_user["password"])

def test_wrong_old_password(client, mock_user):
    token = generate_token(mock_user["email"])
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "oldPassword": "wrongOldPassword",
        "newPassword": "newSecret456"
    }

    response = client.post("password/change_password", json=data, headers=headers)
    assert response.status_code == 401
    assert "Old password is incorrect" in response.json["error"]

def test_missing_token(client):
    data = {
        "oldPassword": "whatever",
        "newPassword": "newSecret456"
    }

    response = client.post("password/change_password", json=data)
    assert response.status_code == 401
    assert "Authorization header" in response.json["error"]

def test_missing_fields(client, mock_user):
    token = generate_token(mock_user["email"])
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "oldPassword": ""
    }

    response = client.post("password/change_password", json=data, headers=headers)
    assert response.status_code == 400
    assert "Old and new password are required" in response.json["error"]

# NEW TESTS FOR BETTER COVERAGE

def test_change_password_expired_token(client, mock_user):
    expired_token = jwt.encode(
        {"email": mock_user["email"], "exp": datetime.datetime.utcnow() - datetime.timedelta(seconds=1)},
        SECRET_KEY,
        algorithm="HS256"
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    data = {
        "oldPassword": mock_user["password"],
        "newPassword": "newSecret456"
    }

    response = client.post("/password/change_password", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json["error"] == "Token expired"

def test_change_password_invalid_token(client):
    headers = {"Authorization": "Bearer not.a.valid.token"}
    data = {
        "oldPassword": "somePassword",
        "newPassword": "newSecret456"
    }

    response = client.post("/password/change_password", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json["error"] == "Invalid token"

def test_change_password_token_missing_email(client):
    token = jwt.encode(
        {"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)},  # no email
        SECRET_KEY,
        algorithm="HS256"
    )
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "oldPassword": "anything",
        "newPassword": "newSecret456"
    }

    response = client.post("/password/change_password", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json["error"] == "Token missing email"

def test_send_reset_email_success(client, mock_user):
    with patch("api.routes_password.send_email") as mock_send_email:
        mock_send_email.return_value = True
        response = client.post("/password/send_reset_email", json={"email": mock_user["email"]})
        assert response.status_code == 200
        assert response.json == {"message": "Reset password link sent"}
        mock_send_email.assert_called_once()

def test_send_reset_email_missing_email(client):
    response = client.post("/password/send_reset_email", json={})
    assert response.status_code == 400
    assert response.json == {"error": "Email is required"}

def test_send_reset_email_user_not_found(client):
    response = client.post("/password/send_reset_email", json={"email": "unknown@example.com"})
    assert response.status_code == 404
    assert response.json == {"error": "User not found"}

def test_send_reset_email_failure(client, mock_user):
    with patch("api.routes_password.send_email", side_effect=Exception("SMTP error")):
        response = client.post("/password/send_reset_email", json={"email": mock_user["email"]})
        assert response.status_code == 500
        assert response.json == {"error": "SMTP error"}

def test_successful_password_reset(client, mock_user):
    token = jwt.encode(
        {
            "email": mock_user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    data = {
        "token": token,
        "newPassword": "MyNewPassword123"
    }

    response = client.post("/password/reset_password", json=data)
    assert response.status_code == 200
    assert response.json["message"] == "Password reset successful."

    updated_user = user_dao.get_user_by_email(mock_user["email"])
    assert bcrypt.checkpw("MyNewPassword123".encode(), updated_user["password"])

def test_reset_password_missing_fields(client):
    response = client.post("/password/reset_password", json={})
    assert response.status_code == 400
    assert response.json["error"] == "Token and new password are required"

def test_reset_password_expired_token(client, mock_user):
    expired_token = jwt.encode(
        {
            "email": mock_user["email"],
            "exp": datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    data = {
        "token": expired_token,
        "newPassword": "NewPass123"
    }

    response = client.post("/password/reset_password", json=data)
    assert response.status_code == 401
    assert response.json["error"] == "Token expired"

def test_reset_password_invalid_token(client):
    data = {
        "token": "not.a.valid.token",
        "newPassword": "AnotherPass123"
    }

    response = client.post("/password/reset_password", json=data)
    assert response.status_code == 401
    assert response.json["error"] == "Invalid token"

def test_reset_password_token_missing_email(client):
    token = jwt.encode(
        {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    data = {
        "token": token,
        "newPassword": "NewerPass456"
    }

    response = client.post("/password/reset_password", json=data)
    assert response.status_code == 401
    assert response.json["error"] == "Token missing email"

def test_reset_password_user_not_found(client):
    email = "nonexistent@example.com"
    token = jwt.encode(
        {
            "email": email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    data = {
        "token": token,
        "newPassword": "AnyPassword789"
    }

    response = client.post("/password/reset_password", json=data)
    assert response.status_code == 404
    assert response.json["error"] == "User not found"