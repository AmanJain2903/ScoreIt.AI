import io
import pytest
from api.app import create_app

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_make_match_valid(client):
    resume_json = {
        "EDUCATION": "Bachelor's in Computer Science",
        "EXPERIENCE": "5 years in software development",
        "TECHNICAL_SKILL": "Python, Java",
        "SOFT_SKILL": "Communication, Teamwork",
        "TOOL": "Git, Docker",
        "CERTIFICATION": "AWS Certified Developer",
        "DESIGNATION": "Software Engineer"
    }
    jd_json = {
        "EDUCATION": "Bachelor's in Computer Science",
        "EXPERIENCE": "3 years in software development",
        "TECHNICAL_SKILL": "Python, Java, SQL",
        "SOFT_SKILL": "Communication, Teamwork, Leadership",
        "TOOL": "Git, Docker, Kubernetes",
        "CERTIFICATION": "AWS Certified Developer",
        "DESIGNATION": "Senior Software Engineer"
    }
    
    response = client.post("/make_match", json={"resume_json": resume_json, "jd_json": jd_json})
    assert response.status_code == 200
    assert 'match_report' in response.get_json()

def test_make_match_invalid_input(client):
    # Test with missing resume_json
    response = client.post("/make_match", json={"jd_json": {}})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid input or missing input"}

    # Test with missing jd_json
    response = client.post("/make_match", json={"resume_json": {}})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid input or missing input"}

    # Test with invalid data types
    response = client.post("/make_match", json={"resume_json": "invalid", "jd_json": "invalid"})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid input or missing input"}

def test_make_match_internal_error(client, monkeypatch):
    def mock_getMatch():
        raise Exception("Internal error")

    monkeypatch.setattr("src.matchmaker_engine.matching_engine.MatchingEngine.getMatch", mock_getMatch)

    resume_json = {
        "EDUCATION": ["Bachelor's in Computer Science"],
        "EXPERIENCE": ["5 years in software development"]
    }
    jd_json = {
        "EDUCATION": ["Bachelor's in Computer Science"],
        "EXPERIENCE": ["3 years in software development"]
    }

    response = client.post("/make_match", json={"resume_json": resume_json, "jd_json": jd_json})
    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal error while processing the input"}



