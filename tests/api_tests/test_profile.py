import io
import pytest
from api.app import create_app
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()


pytestmark = pytest.mark.api
SECRET_KEY = os.getenv("SECRET_KEY")

@pytest.fixture
def client():
    with create_app().test_client() as client:
        yield client

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

def test_create_profile_success(client):
    resp = client.post('/profile/create', json={
        'email': 'test@example.com'
    })
    assert resp.status_code == 201
    assert "message" in resp.json
    token = generate_verification_token('test@example.com')
    resp = client.delete('/profile/delete', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    assert resp.json == {'message': 'Profile deleted'}

def test_create_profile_already_exists(client):
    client.post('/profile/create', json={
        'email': 'test@example.com'
    })
    resp = client.post('/profile/create', json={
        'email': 'test@example.com'
    })
    assert resp.status_code == 400
    assert resp.json == {'error': 'Profile already exists'}
    token = generate_verification_token('test@example.com')
    resp = client.delete('/profile/delete', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    assert resp.json == {'message': 'Profile deleted'}

def test_create_profile_invalid_email(client):
    resp = client.post('/profile/create', json={
        'email': 'test@example'
    })
    assert resp.status_code == 400
    assert resp.json == {'error': 'Invalid email address'}

def test_create_profile_missing_email(client):
    resp = client.post('/profile/create', json={
        'email': ''
    })
    assert resp.status_code == 400
    assert resp.json == {'error': 'Email is required'}

def test_read_profile_success(client):
    client.post('/profile/create', json={
        'email': 'test@example.com'
    })
    token = generate_verification_token('test@example.com')
    resp = client.get('/profile/read', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    token = generate_verification_token('test@example.com')
    resp = client.delete('/profile/delete', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    assert resp.json == {'message': 'Profile deleted'}

def test_read_profile_missing_token(client):
    resp = client.get('/profile/read', headers={
        'Authorization': 'Bearer '
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Token is required'}

def test_read_profile_invalid_token(client):
    resp = client.get('/profile/read', headers={
        'Authorization': 'Fake '
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Authorization header missing or invalid'}

def test_read_profile_missing_email(client):
    resp = client.get('/profile/read', headers={
        'Authorization': f'Bearer {generate_missing_email_token("test@example.com")}'
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Email is required'}

def test_read_profile_missing_profile(client):
    resp = client.get('/profile/read', headers={
        'Authorization': f'Bearer {generate_verification_token("test@example.com")}'
    })
    assert resp.status_code == 404
    assert resp.json == {'error': 'Profile not found'}

def test_update_profile_success(client):
    client.post('/profile/create', json={
        'email': 'test@example.com'
    })
    token = generate_verification_token('test@example.com')
    resp = client.post('/profile/update', 
                       headers={
                           'Authorization': f'Bearer {token}'
                       },
                       json={
                           'update_data': {
                               'dark_mode': True,
                               'model_preference': 2
                           }
                       })
    assert resp.status_code == 200
    assert resp.json == {'message': 'Profile updated'}
    token = generate_verification_token('test@example.com')
    resp = client.delete('/profile/delete', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    assert resp.json == {'message': 'Profile deleted'}

def test_update_profile_missing_token(client):
    resp = client.post('/profile/update', headers={
        'Authorization': 'Bearer '
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Token is required'}

def test_update_profile_invalid_token(client):
    resp = client.post('/profile/update', headers={
        'Authorization': 'Fake '
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Authorization header missing or invalid'}

def test_update_profile_missing_email(client):
    resp = client.post('/profile/update', headers={
        'Authorization': f'Bearer {generate_missing_email_token("test@example.com")}'
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Email is required'}

def test_update_profile_missing_update_data(client):
    resp = client.post('/profile/update', headers={
        'Authorization': f'Bearer {generate_verification_token("test@example.com")}'
    }, json={
        'update_data': {}
    })
    assert resp.status_code == 400
    assert resp.json == {'error': 'Update data is required'}

def test_update_profile_missing_profile(client):
    resp = client.post('/profile/update', headers={
        'Authorization': f'Bearer {generate_verification_token("test@example.com")}'
    }, json={
        'update_data': {"dark_mode": True}
    })
    assert resp.status_code == 404
    assert resp.json == {'error': 'Profile not found or no change'}

def test_delete_profile_success(client):
    client.post('/profile/create', json={
        'email': 'test@example.com'
    })
    token = generate_verification_token('test@example.com')
    resp = client.delete('/profile/delete', headers={
        'Authorization': f'Bearer {token}'
    })
    assert resp.status_code == 200
    assert resp.json == {'message': 'Profile deleted'}

def test_delete_profile_missing_token(client):
    resp = client.delete('/profile/delete', headers={
        'Authorization': 'Bearer '
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Token is required'}

def test_delete_profile_invalid_token(client):
    resp = client.delete('/profile/delete', headers={
        'Authorization': 'Fake '
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Authorization header missing or invalid'}

def test_delete_profile_missing_email(client):
    resp = client.delete('/profile/delete', headers={
        'Authorization': f'Bearer {generate_missing_email_token("test@example.com")}'
    })
    assert resp.status_code == 401
    assert resp.json == {'error': 'Email is required'}

def test_delete_profile_missing_profile(client):
    resp = client.delete('/profile/delete', headers={
        'Authorization': f'Bearer {generate_verification_token("test@example.com")}'
    })
    assert resp.status_code == 404
    assert resp.json == {'error': 'Profile not found'}


