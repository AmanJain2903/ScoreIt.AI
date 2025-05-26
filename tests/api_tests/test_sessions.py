import pytest
from api.app import create_app
from db.sessions_dao import SessionDAO
from db.user_dao import UserDAO
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta
import os

pytestmark = pytest.mark.api
SECRET_KEY = os.getenv("SECRET_KEY")

@pytest.fixture
def client():
    with create_app().test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clear_sessions():
    dao = SessionDAO()
    dao.collection.delete_many({})

@pytest.fixture
def setup_verified_user():
    dao = UserDAO()
    email = "verifytest@example.com"
    # Ensure user exists and is not verified
    try:
        dao.delete_user(email)
    except:
        pass
    dao.create_user(
        name="Verify User",
        email=email,
        password="password123",
        is_google_user=False
    )
    return email

def generate_verification_token(email, expired=False):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=-10 if expired else 30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_create_session_success(client):
    response = client.post('/session/create', json={
        'email': 'user@example.com',
        'token': 'abc123'
    })
    assert response.status_code == 201
    assert response.json == {'message': 'Session created'}

def test_create_session_missing_fields(client):
    response = client.post('/session/create', json={
        'email': 'user@example.com'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and token are required'}

def test_delete_session_success(client):
    client.post('/session/create', json={
        'email': 'user@example.com',
        'token': 'abc123'
    })
    response = client.post('/session/delete', json={
        'email': 'user@example.com',
        'token': 'abc123'
    })
    assert response.status_code == 200
    assert response.json == {'message': 'Session deleted'}

def test_delete_session_missing_fields(client):
    response = client.post('/session/delete', json={
        'token': 'abc123'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and token are required'}

@patch('api.routes_sessions.jwt.decode')
def test_check_session_active(mock_jwt_decode, client):
    mock_jwt_decode.return_value = {'email': 'user@example.com'}
    client.post('/session/create', json={'email': 'user@example.com', 'token': 'abc123'})
    response = client.post('/session/check', json={
        'email': 'user@example.com',
        'token': 'abc123'
    })
    assert response.status_code == 200
    assert response.json == {'active': True}

def test_check_session_inactive(client):
    response = client.post('/session/check', json={
        'email': 'user@example.com',
        'token': 'nonexistent'
    })
    assert response.status_code == 200
    assert response.json == {'active': False}

def test_check_session_missing_fields(client):
    response = client.post('/session/check', json={'email': 'user@example.com'})
    assert response.status_code == 400
    assert response.json == {'error': 'Email and token are required'}

def setup_user_and_session(client, setup_verified_user):
    email = setup_verified_user
    # Register user
    token = generate_verification_token(email)
    response = client.get(f"/verify_email?token={token}")
    assert response.status_code == 200
    assert b"successfully verified" in response.data
    # Login user
    login_resp = client.post("/login", json={"email": email, "password": "password123"})
    token = login_resp.get_json()["token"]
    # Create session
    client.post("/session/create", json={"email": email, "token": token})
    return email, "password123", token

def cleanup_user(client, email, password):
    client.post("/delete", json={"email": email, "password": password})

def test_logout_all_sessions_success(client, setup_verified_user):
    email, password, token = setup_user_and_session(client, setup_verified_user)
    # Check session exists
    assert client.post("/session/check", json={"email": email, "token": token}).get_json()["active"]
    # Logout from all sessions
    logout_resp = client.post("/session/logout_all", json={"email": email, "token": token})
    assert logout_resp.status_code == 200
    assert logout_resp.get_json() == {"message": "Logged out from all devices"}
    # Check session is removed
    assert client.post("/session/check", json={"email": email, "token": token}).get_json()["active"] is False
    cleanup_user(client, email, password)

def test_logout_all_sessions_missing_fields(client):
    resp = client.post("/session/logout_all", json={"email": "someone@example.com"})
    assert resp.status_code == 400
    assert resp.get_json() == {"error": "Email and token are required"}

def test_delete_all_sessions(client):
    # Create multiple sessions
    client.post('/session/create', json={'email': 'user@example.com', 'token': 'abc123'})
    client.post('/session/create', json={'email': 'user@example.com', 'token': 'xyz456'})

    # Delete all
    response = client.post('/session/delete_all', json={'email': 'user@example.com'})
    assert response.status_code == 200
    assert response.json == {'message': 'All sessions deleted'}

def test_delete_all_sessions_missing_email(client):
    response = client.post('/session/delete_all', json={})
    assert response.status_code == 400
    assert response.json == {'error': 'Email is required'}