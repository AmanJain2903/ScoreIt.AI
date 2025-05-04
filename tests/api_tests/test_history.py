import io
import pytest
from api.app import create_app

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_add_history_success(client):
    response = client.post('/history/add', json={
        "email": "xyz@example.com",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"
    assert 'history_id' in response.json
    response = client.delete('/history/delete_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 200

def test_add_history_missing_fields(client):
    response = client.post('/history/add', json={
        "email": "xyz@example.com",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"}
    })
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_add_history_invalid_email(client):
    response = client.post('/history/add', json={
        "email": "xyzexamplecom",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_add_history_invalid_data_types(client):
    response = client.post('/history/add', json={
        "email": "xyz@example.com",
        "resume_text": 123,
        "resume_json": "Invalid JSON",
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid data types"

def test_get_all_history_success(client):
    response = client.post('/history/add', json={
        "email": "xyz@example.com",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"

    response = client.get('/history/get_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 200
    assert 'history' in response.json
    assert isinstance(response.json['history'], list)

    response = client.delete('/history/delete_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 200

def test_get_all_history_missing_fields(client):
    response = client.get('/history/get_all', json={})
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_get_all_history_invalid_email(client):
    response = client.get('/history/get_all', json={
        "email": "xyzexamplecom"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_get_all_history_no_history_found(client):
    response = client.get('/history/get_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 404
    assert response.json['message'] == "No history found"

def test_delete_one_history_success(client):
    response = client.post('/history/add', json={
        "email": "xyz@example.com",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"
    assert 'history_id' in response.json
    
    response = client.delete('/history/delete_one', json={
        "email": "xyz@example.com",
        "match_id": response.json['history_id']
    })
    assert response.status_code == 200
    assert response.json['message'] == "Match report deleted successfully"

def test_delete_one_history_missing_fields(client):
    response = client.delete('/history/delete_one', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_delete_one_history_invalid_email(client):
    response = client.delete('/history/delete_one', json={
        "email": "xyzexamplecom",
        "match_id": "1234567890abcdef12345678"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_delete_one_history_no_match_found(client):
    response = client.delete('/history/delete_one', json={
        "email": "xyz@example.com",
        "match_id": "1234567890abcdef12345678"
    })
    assert response.status_code == 404
    assert response.json['error'] == "No match report found with the given ID"

def test_delete_all_history_success(client):
    response = client.post('/history/add', json={
        "email": "xyz@example.com",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 200
    assert response.json['message'] == "History added successfully"
    assert 'history_id' in response.json
    response = client.delete('/history/delete_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 200

def test_delete_all_history_no_history_found(client):
    response = client.delete('/history/delete_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 404
    assert response.json['message'] == "No history records found to delete"

def test_delete_all_history_missing_fields(client):
    response = client.delete('/history/delete_all', json={})
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_delete_all_history_invalid_email(client):
    response = client.delete('/history/delete_all', json={
        "email": "xyzexamplecom"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"


