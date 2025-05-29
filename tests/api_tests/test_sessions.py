import pytest
from api.app import create_app
from db.sessions_dao import SessionDAO
from db.user_dao import UserDAO
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta
import os
from jwt.exceptions import InvalidTokenError

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

def generate_missing_email_token(email):
    payload = {
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@pytest.fixture
def setup_verified_user():
    dao = UserDAO()
    email = "xyz@example.com"
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
    token = generate_verification_token("xyz@example.com")
    response = client.post('/session/create', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 201
    assert response.json == {'message': 'Session created'}

def test_create_session_missing_fields(client):
    token = generate_missing_email_token("xyz@example.com")
    response = client.post('/session/create', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and token are required'}

def test_create_session_invalid_token(client):
    response = client.post('/session/create', headers={
        'Authorization': "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid token'}

def test_create_session_missing_token(client):
    response = client.post('/session/create', headers={
        'Authorization': "Fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Authorization header missing or invalid'}

def test_delete_session_success(client):
    token = generate_verification_token("xyz@example.com")
    client.post('/session/create', headers={
        'Authorization': f"Bearer {token}"
    })
    response = client.delete('/session/delete', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json == {'message': 'Session deleted'}

def test_delete_session_missing_fields(client):
    token = generate_missing_email_token("xyz@example.com")
    response = client.delete('/session/delete', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and token are required'}

def test_delete_session_invalid_token(client):
    response = client.delete('/session/delete', headers={
        'Authorization': "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid token'}

def test_delete_session_missing_token(client):
    response = client.delete('/session/delete', headers={
        'Authorization': "Fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Authorization header missing or invalid'}

@patch('api.routes_sessions.jwt.decode')
def test_check_session_active(mock_jwt_decode, client):
    mock_jwt_decode.return_value = {'email': 'xyz@example.com'}
    token = generate_verification_token("xyz@example.com")
    client.post('/session/create', headers={
        'Authorization': f"Bearer {token}"
    })
    response = client.get('/session/check', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json == {'active': True}
    client.delete('/session/delete_all', headers={
        'Authorization': f"Bearer {token}"
    })

def test_check_session_inactive(client):
    token = generate_verification_token("xyz@example.com")  
    response = client.get('/session/check', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json == {'active': False}

def test_check_session_missing_fields(client):
    token = generate_missing_email_token("xyz@example.com")
    response = client.get('/session/check', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and token are required'}

def test_check_session_invalid_token(client):
    response = client.get('/session/check', headers={
        'Authorization': "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid token'}

def test_check_session_missing_token(client):
    response = client.get('/session/check', headers={
        'Authorization': "Fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Authorization header missing or invalid'}

def test_delete_all_sessions(client):
    # Create multiple sessions
    token = generate_verification_token("xyz@example.com")
    client.post('/session/create', headers={
        'Authorization': f"Bearer {token}"
    })
    token = generate_verification_token("xyz@example.com")
    client.post('/session/create', headers={
        'Authorization': f"Bearer {token}"
    })

    # Delete all
    response = client.delete('/session/delete_all', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json == {'message': 'All sessions deleted'}

def test_delete_all_sessions_missing_email(client):
    token = generate_missing_email_token("xyz@example.com")
    response = client.delete('/session/delete_all', headers={
        'Authorization': f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email is required'}

def test_delete_all_sessions_invalid_token(client):
    response = client.delete('/session/delete_all', headers={
        'Authorization': "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid token'}

def test_delete_all_sessions_missing_token(client):
    response = client.delete('/session/delete_all', headers={
        'Authorization': "Fake"
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Authorization header missing or invalid'}


# NEW TESTS FOR BETTER COVERAGE

@patch("api.routes_sessions.jwt.decode")
def test_check_session_invalid_token_after_active(mock_decode, client):
    email = "xyz@example.com"
    token = jwt.encode({
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=5)
    }, SECRET_KEY, algorithm="HS256")

    SessionDAO().create_session(email, token)

    # First call succeeds, second raises signature error
    mock_decode.side_effect = [ {"email": email}, InvalidTokenError("Invalid") ]

    response = client.get('/session/check', headers={
        'Authorization': f"Bearer {token}"
    })

    assert response.status_code == 200
    assert response.json == {"active": False}

    SessionDAO().delete_session(email, token)

@patch("api.routes_sessions.jwt.decode")
def test_check_session_unexpected_exception_after_active(mock_decode, client):
    email = "xyz@example.com"
    token = jwt.encode({
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=5)
    }, SECRET_KEY, algorithm="HS256")

    SessionDAO().create_session(email, token)

    # First decode works, second throws Exception
    mock_decode.side_effect = [ {"email": email}, Exception("Unexpected crash") ]

    response = client.get('/session/check', headers={
        'Authorization': f"Bearer {token}"
    })

    assert response.status_code == 200
    assert response.json == {"active": False}

    SessionDAO().delete_session(email, token)

