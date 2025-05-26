import io
import pytest
from api.app import create_app
from unittest.mock import patch, MagicMock
from db.user_dao import UserDAO
import jwt
from datetime import datetime, timedelta
import os

pytestmark = pytest.mark.api
SECRET_KEY = os.getenv("SECRET_KEY")

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

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

# Dummy Google payload
MOCK_GOOGLE_ID_INFO = {
    "email": "testuser@example.com",
    "name": "Test User"
}

@pytest.fixture
def client():
    with create_app().test_client() as client:
        yield client

def test_register_success(client):
    response = client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 201
    assert response.json == {'message': 'User registered successfully'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_register_missing_email(client):
    response = client.post('/register', json={
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}

def test_register_missing_password(client):
    response = client.post('/register', json={
        'email': 'xyz@example.com',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}

def test_register_invalid_email(client):
    response = client.post('/register', json={
        'email': 'invalid-email',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 553
    assert response.json == {'error': 'Invalid email format'}

def test_register_email_already_registered(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 409
    assert response.json == {'error': 'Email already registered'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_success(client, setup_verified_user):
    email = setup_verified_user
    token = generate_verification_token(email)
    response = client.get(f"/verify_email?token={token}")
    assert response.status_code == 200
    assert b"successfully verified" in response.data
    response = client.post('/login', json={
        'email': email,
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.json
    response = client.post('/delete', json={
        'email': email,
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_unverified_user(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/login', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Please verify your email to login'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_missing_email(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/login', json={
        'password': 'password123'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_missing_password(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/login', json={
        'email': 'xyz@example.com'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_user_not_found(client):
    response = client.post('/login', json={
        'email': 'abc@example.com',
        'password': 'password123'
    })
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}

def test_login_invalid_credentials(client, setup_verified_user):
    email = setup_verified_user
    token = generate_verification_token(email)
    response = client.get(f"/verify_email?token={token}")
    assert response.status_code == 200
    assert b"successfully verified" in response.data
    response = client.post('/login', json={
        'email': email,
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid credentials'}
    response = client.post('/delete', json={
        'email': email,
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_success(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_missing_email(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/delete', json={
        'password': 'password123'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_missing_password(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/delete', json={
        'email': 'xyz.example.com'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_user_not_found(client):
    response = client.post('/delete', json={
        'email': 'fake@fake.com',
        'password': 'password123'
    })
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}

def test_delete_invalid_credentials(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid credentials'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

@patch("api.routes_auth.requests.get")
def test_google_login_new_user(mock_get, client):
    # Mock Google userinfo API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "email": "testuser@example.com",
        "name": "Test User"
    }
    mock_get.return_value = mock_response

    response = client.post("/google", json={
        "access_token": "dummy_token"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"
    assert data["is_google_user"] is True
    assert "token" in data
    assert "dark_mode" in data
    # Clean up
    client.post('/delete', json={
        'email': 'testuser@example.com',
        'password': 'dummy_token'
    })

@patch("api.routes_auth.requests.get")
def test_google_login_existing_google_user(mock_get, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "email": "testuser@example.com",
        "name": "Test User"
    }
    mock_get.return_value = mock_response

    # First create user
    client.post("/google", json={"access_token": "dummy_token"})

    # Login again
    response = client.post("/google", json={"access_token": "dummy_token"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Test User"
    assert data["is_google_user"] is True
    assert "token" in data
    assert "dark_mode" in data
    # Clean up
    client.post('/delete', json={
        'email': 'testuser@example.com',
        'password': 'dummy_token'
    })

@patch("api.routes_auth.requests.get")
def test_google_login_existing_non_google_user(mock_get, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "email": "existing@normal.com",
        "name": "Non Google User"
    }
    mock_get.return_value = mock_response

    # Insert a fake non-Google user manually
    user_collection = UserDAO().collection
    user_collection.insert_one({
        "name": "Non Google User",
        "email": "existing@normal.com",
        "password": "hashed",
        "is_google_user": False
    })

    response = client.post("/google", json={"access_token": "dummy_token"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "User already registered. Login with Password instead."
    user_collection.delete_one({
        "email": "existing@normal.com"
    })

def test_google_login_missing_token(client):
    response = client.post("/google", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing token"

@patch("api.routes_auth.requests.get")
def test_google_login_invalid_token(mock_get, client):
    # Simulate Google userinfo API returning no email
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    response = client.post("/google", json={"access_token": "bad_token"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid token payload"

@patch("api.routes_auth.requests.get")
def test_delete_google_user_success(mock_get, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "email": "testuser@example.com",
        "name": "Test User"
    }
    mock_get.return_value = mock_response

    response = client.post("/google", json={"access_token": "dummy_token"})
    assert response.status_code == 200
    delete_response = client.post('/delete', json={
        'email': 'testuser@example.com',
        'password': 'dummy_token'
    })
    assert delete_response.status_code == 200
    assert delete_response.json == {'message': 'User deleted successfully'}

def test_update_success(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/update', json={
        'email': 'xyz@example.com',
    })
    assert response.status_code == 200
    assert response.json == {'message': 'User updated successfully'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_update_user_not_found(client):
    response = client.post('/update', json={
        'email': 'xyz@example.com',
        'dark_mode': True
    })
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}

def test_update_missing_email(client):
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/update', json={
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email is required'}
    response = client.post('/delete', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

@patch("api.routes_auth.send_email")
def test_send_verification_success(mock_send_email, client):
    mock_send_email.return_value = None 

    client.post('/register', json={
        'email': 'testuser@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })

    response = client.post("/send_email", json={
        "email": "testuser@example.com"
    })

    assert response.status_code == 200
    assert response.json == {"message": "Verification email sent"}
    mock_send_email.assert_called_once()
    response = client.post('/delete', json={
        'email': 'testuser@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_send_verification_missing_email(client):
    response = client.post("/send_email", json={})
    assert response.status_code == 400
    assert response.json == {"error": "Email is required"}

def test_send_verification_invalid_email(client):
    response = client.post("/send_email", json={
        "email": "invalid-email"
    })
    assert response.status_code == 400 or 553

def test_verify_email_success(client, setup_verified_user):
    token = generate_verification_token(setup_verified_user)
    response = client.get(f"/verify_email?token={token}")
    assert response.status_code == 200
    assert b"successfully verified" in response.data
    response = client.post('/delete', json={
        'email': 'verifytest@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_verify_email_expired(client, setup_verified_user):
    token = generate_verification_token(setup_verified_user, expired=True)
    response = client.get(f"/verify_email?token={token}")
    assert response.status_code == 400
    assert b"expired" in response.data
    response = client.post('/delete', json={
        'email': 'verifytest@example.com',
        'password': 'password123'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_verify_email_invalid_token(client):
    response = client.get("/verify_email?token=invalidtoken123")
    assert response.status_code == 400
    assert b"expired" in response.data or b"Invalid" in response.data

def test_verify_email_user_not_found(client):
    email = "nonexistent@example.com"
    token = generate_verification_token(email)
    response = client.get(f"/verify_email?token={token}")
    assert response.status_code == 404
    assert b"User not found" in response.data


