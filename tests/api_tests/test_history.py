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

def test_add_history_internal_server_error(client, monkeypatch):
    def mock_save_history(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.save_history', mock_save_history)

    response = client.post('/history/add', json={
        "email": "xyz@example.com",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to save history"

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

    response = client.post('/history/get_all', json={
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
    response = client.post('/history/get_all', json={})
    assert response.status_code == 400
    assert response.json['error'] == "Missing required fields"

def test_get_all_history_invalid_email(client):
    response = client.post('/history/get_all', json={
        "email": "xyzexamplecom"
    })
    assert response.status_code == 400
    assert response.json['error'] == "Invalid email format"

def test_get_all_history_no_history_found(client):
    response = client.post('/history/get_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 200
    assert response.json['message'] == "No history found"

def test_get_all_history_internal_server_error(client, monkeypatch):
    def mock_get_history(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.get_history', mock_get_history)

    response = client.post('/history/get_all', json={
        "email": "xyz@example.com",
        "resume_text": "Sample resume text",
        "resume_json": {"key": "value"},
        "jd_text": "Sample job description text",
        "jd_json": {"key": "value"},
        "match_report": {"key": "value"}
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to retrieve history"

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

def test_delete_one_history_internal_server_error(client, monkeypatch):
    def mock_delete_match_by_id(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.delete_match_by_id', mock_delete_match_by_id)

    response = client.delete('/history/delete_one', json={
        "email": "xyz@example.com",
        "match_id": "1234567890abcdef12345678"
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to delete match report"

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
    assert response.status_code == 200
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

def test_delete_all_history_internal_server_error(client, monkeypatch):
    def mock_delete_all_history(*args, **kwargs):
        raise Exception("Database error")

    monkeypatch.setattr('api.routes_history.history_dao.clear_history', mock_delete_all_history)

    response = client.delete('/history/delete_all', json={
        "email": "xyz@example.com"
    })
    assert response.status_code == 500
    assert response.json['error'] == "Failed to delete history records"


