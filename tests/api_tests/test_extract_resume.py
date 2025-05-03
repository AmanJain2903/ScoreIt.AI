import io
import pytest
from api.app import create_app

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_extract_resume_valid(client):
    resume_text = "John Doe\nSoftware Engineer\nExperience: 5 years\nSkills: Python, Flask"
    response = client.post('/extract_resume', data={'resume_text': resume_text})
    assert response.status_code == 200
    assert 'resume_entites' in response.get_json()

def test_extract_resume_missing(client):
    response = client.post('/extract_resume', data={'resume_text': None})
    assert response.status_code == 400
    assert response.json['error'] == "Invalid input or missing text"

def test_extract_resume_internal_error(client, monkeypatch):
    def mock_get_json_output():
        raise Exception("Internal error")
    
    monkeypatch.setattr('src.resume_extractor_agent.resume_agent.ResumeAgent.getJsonOutput', mock_get_json_output)
    
    resume_text = "John Doe\nSoftware Engineer\nExperience: 5 years\nSkills: Python, Flask"
    response = client.post('/extract_resume', data={'resume_text': resume_text})
    assert response.status_code == 500
    assert response.json['error'] == "Internal error while processing the text"



