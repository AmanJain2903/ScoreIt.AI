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

def generate_missing_email_token(email):
    payload = {
        "exp": datetime.utcnow() + timedelta(minutes=30)
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
    response = client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 201
    assert response.json == {'message': 'User registered successfully'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_register_missing_email(client):
    response = client.post('auth/register', json={
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}

def test_register_missing_password(client):
    response = client.post('auth/register', json={
        'email': 'xyz@example.com',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}

def test_register_invalid_email(client):
    response = client.post('auth/register', json={
        'email': 'invalid-email',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 553
    assert response.json == {'error': 'Invalid email format'}

def test_register_email_already_registered(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 409
    assert response.json == {'error': 'Email already registered'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_success(client, setup_verified_user):
    email = setup_verified_user
    token = generate_verification_token(email)
    response = client.get(f"auth/verify_email?token={token}")
    assert response.status_code == 200
    assert b"successfully verified" in response.data
    response = client.post('auth/login', json={
        'email': email,
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'token' in response.json
    token = generate_verification_token(email)
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_unverified_user(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('auth/login', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Please verify your email to login'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_missing_email(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('auth/login', json={
        'password': 'password123'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_missing_password(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('auth/login', json={
        'email': 'xyz@example.com'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_login_user_not_found(client):
    response = client.post('auth/login', json={
        'email': 'abc@example.com',
        'password': 'password123'
    })
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}

def test_login_invalid_credentials(client, setup_verified_user):
    email = setup_verified_user
    token = generate_verification_token(email)
    response = client.get(f"auth/verify_email?token={token}")
    assert response.status_code == 200
    assert b"successfully verified" in response.data
    response = client.post('auth/login', json={
        'email': email,
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid credentials'}
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_success(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_missing_email(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    token = generate_missing_email_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Token missing email'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_missing_password(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': None
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Password is required'}
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_delete_user_not_found(client):
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}

def test_delete_invalid_credentials(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'wrongpassword'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid credentials'}
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
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

    response = client.post("auth/google", json={
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
    token = generate_verification_token('testuser@example.com')
    client.post('auth/delete', json={
        'password': 'dummy_token'
    }, headers={
        'Authorization': f'Bearer {token}'
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
    client.post("auth/google", json={"access_token": "dummy_token"})

    # Login again
    response = client.post("auth/google", json={"access_token": "dummy_token"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Test User"
    assert data["is_google_user"] is True
    assert "token" in data
    assert "dark_mode" in data
    # Clean up
    token = generate_verification_token('testuser@example.com')
    client.post('auth/delete', json={
        'password': 'dummy_token'
    }, headers={
        'Authorization': f'Bearer {token}'
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

    response = client.post("auth/google", json={"access_token": "dummy_token"})
    assert response.status_code == 400
    assert response.get_json()["error"] == "User already registered. Login with Password instead."
    user_collection.delete_one({
        "email": "existing@normal.com"
    })

def test_google_login_missing_token(client):
    response = client.post("auth/google", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing token"

@patch("api.routes_auth.requests.get")
def test_google_login_invalid_token(mock_get, client):
    # Simulate Google userinfo API returning no email
    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    response = client.post("auth/google", json={"access_token": "bad_token"})
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

    response = client.post("auth/google", json={"access_token": "dummy_token"})
    assert response.status_code == 200
    token = generate_verification_token('testuser@example.com')
    delete_response = client.post('auth/delete', json={
        'password': 'dummy_token'
    }, headers={
        'Authorization': f'Bearer {token}'
    })
    assert delete_response.status_code == 200
    assert delete_response.json == {'message': 'User deleted successfully'}

def test_update_success(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/update', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json == {'message': 'User updated successfully'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_update_user_not_found(client):
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/update', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}

def test_update_missing_email(client):
    client.post('auth/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    token = generate_missing_email_token('xyz@example.com') 
    response = client.post('auth/update', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Token missing email'}
    token = generate_verification_token('xyz@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

@patch("api.routes_auth.send_email")
def test_send_verification_success(mock_send_email, client):
    mock_send_email.return_value = None 

    client.post('auth/register', json={
        'email': 'testuser@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })

    response = client.post("auth/send_email", json={
        "email": "testuser@example.com"
    })

    assert response.status_code == 200
    assert response.json == {"message": "Verification email sent"}
    mock_send_email.assert_called_once()
    token = generate_verification_token('testuser@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_send_verification_missing_email(client):
    response = client.post("auth/send_email", json={})
    assert response.status_code == 400
    assert response.json == {"error": "Email is required"}

def test_send_verification_invalid_email(client):
    response = client.post("auth/send_email", json={
        "email": "invalid-email"
    })
    assert response.status_code == 400 or 553

def test_verify_email_success(client, setup_verified_user):
    token = generate_verification_token(setup_verified_user)
    response = client.get(f"auth/verify_email?token={token}")
    assert response.status_code == 200
    assert b"successfully verified" in response.data
    token = generate_verification_token('verifytest@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_verify_email_expired(client, setup_verified_user):
    token = generate_verification_token(setup_verified_user, expired=True)
    response = client.get(f"auth/verify_email?token={token}")
    assert response.status_code == 400
    assert b"expired" in response.data
    token = generate_verification_token('verifytest@example.com')
    response = client.post('auth/delete', json={
        'password': 'password123'
    }, headers={
        'Authorization': f'Bearer {token}'
    })  # Clean up after test
    assert response.status_code == 200
    assert response.json == {'message': 'User deleted successfully'}

def test_verify_email_invalid_token(client):
    response = client.get("auth/verify_email?token=invalidtoken123")
    assert response.status_code == 400
    assert b"expired" in response.data or b"Invalid" in response.data

def test_verify_email_user_not_found(client):
    email = "nonexistent@example.com"
    token = generate_verification_token(email)
    response = client.get(f"auth/verify_email?token={token}")
    assert response.status_code == 404
    assert b"User not found" in response.data

def test_delete_invalid_token(client):
    response = client.post('auth/delete', headers={
        'Authorization': "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Invalid token"

def test_delete_missing_token(client):
    response = client.post('auth/delete', headers={
        'Authorization': "Fake {123}"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Authorization header missing or invalid"

def test_update_invalid_token(client):
    response = client.post('auth/update', headers={
        'Authorization': "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Invalid token"

def test_update_missing_token(client):
    response = client.post('auth/update', headers={
        'Authorization': "Fake {123}"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Authorization header missing or invalid"

def test_update_invalid_token(client):
    response = client.post('auth/update', json={
        'email': "xyz@example.com"
    }, headers={
        'Authorization': "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Invalid token"

# NEW TESTS FOR BETTER COVERAGE

@patch("api.routes_auth.requests.get")
def test_google_login_value_error(mock_get, client):
    # Mock the request to raise a ValueError during Google call
    mock_get.side_effect = ValueError("Invalid value")

    response = client.post("/auth/google", json={"access_token": "fake_token"})
    
    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid token"

@patch("api.routes_auth.requests.get")
def test_google_login_unexpected_exception(mock_get, client):
    # Raise a general exception
    mock_get.side_effect = Exception("Unexpected failure")

    response = client.post("/auth/google", json={"access_token": "fake_token"})

    assert response.status_code == 500
    assert "Unexpected failure" in response.get_json()["error"]

def test_register_email_already_registered_google_user(client):
    # Insert a mock Google user
    user_collection = UserDAO().collection
    user_collection.insert_one({
        "name": "Google User",
        "email": "googleuser@example.com",
        "password": "",  # irrelevant for Google
        "is_google_user": True,
        "verified": True
    })

    # Attempt to register with the same email using password
    response = client.post('/auth/register', json={
        'email': 'googleuser@example.com',
        'password': 'somepassword123',
        'name': 'Google User Attempt'
    })

    assert response.status_code == 409
    assert response.json == {'error': 'Email already registered. Login with Google instead.'}

    # Cleanup
    user_collection.delete_one({"email": "googleuser@example.com"})

def test_login_google_registered_user(client):
    user_collection = UserDAO().collection

    # Insert Google user directly
    user_collection.insert_one({
        "name": "Google Guy",
        "email": "googlelogin@example.com",
        "password": "",  # No password for Google users
        "is_google_user": True,
        "verified": True,
        "dark_mode": False
    })

    # Try logging in with password
    response = client.post('/auth/login', json={
        "email": "googlelogin@example.com",
        "password": "doesnotmatter"
    })

    assert response.status_code == 409
    assert response.json == {"error": "Login with Google instead."}

    # Cleanup
    user_collection.delete_one({"email": "googlelogin@example.com"})

@patch("api.routes_auth.requests.get")
def test_delete_google_user_invalid_email(mock_get, client):
    # Insert Google user
    user_collection = UserDAO().collection
    email = "googlewrong@example.com"
    user_collection.insert_one({
        "name": "Wrong Google User",
        "email": email,
        "is_google_user": True
    })

    # Mock Google's userinfo to return a *different* email
    mock_response = MagicMock()
    mock_response.json.return_value = {"email": "wrong@example.com"}
    mock_get.return_value = mock_response

    token = jwt.encode({"email": email, "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")

    response = client.post("/auth/delete", json={"password": "dummy_token"}, headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 401
    assert response.json == {"error": "Invalid credentials"}

    user_collection.delete_one({"email": email})

from unittest.mock import patch

@patch("api.routes_auth.send_email")
def test_send_verification_email_failure(mock_send_email, client):
    # Simulate send_email raising an exception
    mock_send_email.side_effect = Exception("SMTP error")

    # Register a user so that `get_user_by_email()` works
    client.post('auth/register', json={
        'email': 'failmail@example.com',
        'password': 'password123',
        'name': 'Fail Test'
    })

    # Trigger the endpoint
    response = client.post("/auth/send_email", json={
        "email": "failmail@example.com"
    })

    assert response.status_code == 500
    assert "SMTP error" in response.get_json()["error"]

    # Clean up
    token = jwt.encode({"email": "failmail@example.com", "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
    client.post("/auth/delete", json={"password": "password123"}, headers={"Authorization": f"Bearer {token}"})

def test_verify_email_missing_token(client):
    response = client.get("/auth/verify_email")  # No token query param
    assert response.status_code == 400
    assert b"Invalid verification link" in response.data

def test_verify_email_missing_email_in_token(client):
    token = jwt.encode({"exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
    response = client.get(f"/auth/verify_email?token={token}")
    assert response.status_code == 400
    assert b"Invalid token payload" in response.data

def test_verify_email_user_not_found(client):
    token = jwt.encode({"email": "ghost@example.com", "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
    response = client.get(f"/auth/verify_email?token={token}")
    assert response.status_code == 404
    assert b"User not found" in response.data

def test_verify_email_invalid_token_signature(client):
    response = client.get("/auth/verify_email?token=invalidtoken123")
    assert response.status_code == 400
    assert b"Invalid verification token" in response.data

from unittest.mock import patch

@patch("api.routes_auth.user_dao.get_user_by_email")
def test_verify_email_unexpected_error(mock_get_user, client):
    mock_get_user.side_effect = Exception("DB crash")

    token = jwt.encode({"email": "abc@example.com", "exp": datetime.utcnow() + timedelta(minutes=30)}, SECRET_KEY, algorithm="HS256")
    response = client.get(f"/auth/verify_email?token={token}")

    assert response.status_code == 500
    assert b"Error" in response.data
    assert b"DB crash" in response.data