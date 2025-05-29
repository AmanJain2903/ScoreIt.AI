import io
import pytest
from api.app import create_app
import jwt
import os
from datetime import datetime, timedelta

pytestmark = pytest.mark.api

SECRET_KEY = os.getenv("SECRET_KEY")

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

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

def test_add_history_success(client):
    token = generate_verification_token("xyz@example.com")
    response = client.post('/history/add', json={
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"
    assert 'history_id' in response.json
    token = generate_verification_token("xyz@example.com")
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200

def test_add_history_missing_fields(client):
    token = generate_verification_token("xyz@example.com")
    response = client.post('/history/add', json={
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_add_history_invalid_email(client):
    token = generate_verification_token("xyzexamplecom")
    response = client.post('/history/add', json={
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_add_history_invalid_data_types(client):
    token = generate_verification_token("xyz@example.com")
    response = client.post('/history/add', json={
        "resume_text": 123,
        "resume_json": "Invalid JSON",
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid data types"

def test_add_history_internal_server_error(client, monkeypatch):
    def mock_save_history(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.save_history', mock_save_history)

    token = generate_verification_token("xyz@example.com")
    response = client.post('/history/add', json={
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to save history"

def test_get_all_history_success(client):
    token = generate_verification_token("xyz@example.com")
    response = client.post('/history/add', json={
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"
    token = generate_verification_token("xyz@example.com")
    response = client.get('/history/get_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert 'history' in response.json
    assert isinstance(response.json['history'], list)

    token = generate_verification_token("xyz@example.com")  
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200

def test_get_all_history_missing_fields(client):
    token = generate_missing_email_token("xyz@example.com")
    response = client.get('/history/get_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_get_all_history_invalid_email(client):
    token = generate_verification_token("xyzexamplecom")
    response = client.get('/history/get_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_get_all_history_no_history_found(client):
    token = generate_verification_token("xyz@example.com")  
    response = client.get('/history/get_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json['message'] == "No history found"

def test_get_all_history_internal_server_error(client, monkeypatch):
    def mock_get_history(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.get_history', mock_get_history)

    token = generate_verification_token("xyz@example.com")
    response = client.get('/history/get_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to retrieve history"

def test_delete_one_history_success(client):
    token = generate_verification_token("xyz@example.com")
    response = client.post('/history/add', json={
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"
    assert 'history_id' in response.json
    token = generate_verification_token("xyz@example.com")
    response = client.delete('/history/delete_one', json={
        "match_id": response.json['history_id']
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json['message'] == "Match report deleted successfully"

def test_delete_one_history_missing_fields(client):
    token = generate_verification_token("xyz@example.com")
    response = client.delete('/history/delete_one', json={
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_delete_one_history_invalid_email(client):
    token = generate_verification_token("xyzexamplecom")
    response = client.delete('/history/delete_one', json={
        "match_id": "1234567890abcdef12345678"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_delete_one_history_no_match_found(client):
    token = generate_verification_token("xyz@example.com")
    response = client.delete('/history/delete_one', json={
        "match_id": "1234567890abcdef12345678"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 404
    assert response.json['error'] == "No match report found with the given ID"

def test_delete_one_history_internal_server_error(client, monkeypatch):
    def mock_delete_match_by_id(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.delete_match_by_id', mock_delete_match_by_id)

    token = generate_verification_token("xyz@example.com")  
    response = client.delete('/history/delete_one', json={
        "match_id": "1234567890abcdef12345678"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to delete match report"

def test_delete_all_history_success(client):
    token = generate_verification_token("xyz@example.com")
    response = client.post('/history/add', json={
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"
    assert 'history_id' in response.json
    token = generate_verification_token("xyz@example.com")
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200

def test_delete_all_history_no_history_found(client):
    token = generate_verification_token("xyz@example.com")
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json['message'] == "No history records found to delete"

def test_delete_all_history_missing_fields(client):
    token = generate_missing_email_token("xyz@example.com")
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_delete_all_history_invalid_email(client):
    token = generate_verification_token("xyzexamplecom")
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_delete_all_history_internal_server_error(client, monkeypatch):
    def mock_delete_all_history(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.clear_history', mock_delete_all_history)
    token = generate_verification_token("xyz@example.com")
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to delete history records"

def test_delete_all_history_invalid_token(client):
    response = client.delete('/history/delete_all', headers={
        "Authorization": "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Invalid token"

def test_delete_all_history_missing_token(client):
    response = client.delete('/history/delete_all', headers={
        "Authorization": f"Fake{123}"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Authorization header missing or invalid"

def test_delete_one_history_invalid_token(client):
    response = client.delete('/history/delete_one', headers={
        "Authorization": "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Invalid token"

def test_delete_one_history_missing_token(client):
    response = client.delete('/history/delete_one', headers={
        "Authorization": f"Fake{123}"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Authorization header missing or invalid"

def test_get_all_history_invalid_token(client):
    response = client.get('/history/get_all', headers={
        "Authorization": "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Invalid token"

def test_get_all_history_missing_token(client):
    response = client.get('/history/get_all', headers={
        "Authorization": f"Fake{123}"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Authorization header missing or invalid"

def test_add_history_invalid_token(client):
    response = client.post('/history/add', headers={
        "Authorization": "Bearer fake"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Invalid token"

def test_add_history_missing_token(client):
    response = client.post('/history/add', headers={
        "Authorization": f"Fake{123}"
    })
    assert response.status_code == 401
    assert response.json['error'] == "Authorization header missing or invalid"
