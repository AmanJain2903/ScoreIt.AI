import io
import pytest
from api.app import create_app
from api.routes_auth import users

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_register_success(client):
    users.clear()  # Clear any existing users
    response = client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 201
    assert response.json == {'message': 'User registered successfully'}

def test_register_missing_email(client):
    users.clear()  # Clear any existing users
    response = client.post('/register', json={
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}

def test_register_missing_password(client):
    users.clear()  # Clear any existing users
    response = client.post('/register', json={
        'email': 'xyz@example.com',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 400
    assert response.json == {'error': 'Email and password are required'}

def test_register_invalid_email(client):
    users.clear()  # Clear any existing users
    response = client.post('/register', json={
        'email': 'invalid-email',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    assert response.status_code == 553
    assert response.json == {'error': 'Invalid email format'}

def test_register_email_already_registered(client):
    users.clear()  # Clear any existing users
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

def test_login_success(client):
    users.clear()  # Clear any existing users
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/login', json={
        'email': 'xyz@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200

def test_login_missing_email(client):
    users.clear()  # Clear any existing users
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

def test_login_missing_password(client):
    users.clear()  # Clear any existing users
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

def test_login_user_not_found(client):
    users.clear()  # Clear any existing users
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/login', json={
        'email': 'abc@example.com',
        'password': 'password123'
    })
    assert response.status_code == 404
    assert response.json == {'error': 'User not found'}

def test_login_invalid_credentials(client):
    users.clear()  # Clear any existing users
    client.post('/register', json={
        'email': 'xyz@example.com',
        'password': 'password123',
        'name': 'Lorem Ipsum'
    })
    response = client.post('/login', json={
        'email': 'xyz@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid credentials'}
