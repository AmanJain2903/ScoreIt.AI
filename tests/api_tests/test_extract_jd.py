import io
import pytest
from api.app import create_app

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_extract_jd_valid(client):
    data = {
        "jd_text": "We are looking for a software engineer with experience in Python and Flask."
    }
    response = client.post("/extract_jd", data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "jd_entites" in json_data

def test_extract_jd_missing_text(client):
    data = {
        "jd_text": None
    }
    response = client.post("/extract_jd", data=data)
    assert response.status_code == 400
    assert response.json['error'] == "Invalid input or missing text"

def test_extract_jd_internal_error(client, monkeypatch):
    def mock_get_json_output():
        raise Exception("Internal error")
    
    monkeypatch.setattr('src.jd_extractor_agent.jd_agent.JobDescriptionAgent.getJsonOutput', mock_get_json_output)
    
    jd_text = "We are looking for a software engineer with experience in Python and Flask."
    response = client.post('/extract_jd', data={'jd_text': jd_text})
    assert response.status_code == 500
    assert response.json['error'] == "Internal error while processing the text"



