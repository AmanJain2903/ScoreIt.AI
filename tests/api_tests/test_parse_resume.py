import io
import pytest
from api.app import create_app

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_parse_resume_valid_pdf(client):
    with open("data/pdf_resumes/cv (1).pdf", "rb") as f:
        data = {'resume_file': (io.BytesIO(f.read()), "cv (1).pdf")}
        response = client.post("/parse_resume", content_type='multipart/form-data', data=data)
        assert response.status_code == 200
        assert "resume_text" in response.json

def test_parse_resume_no_input(client):
    data = {'resume_file': None}
    response = client.post("/parse_resume", content_type='multipart/form-data', data=data)
    assert response.status_code == 400
    assert response.json["error"] == "Invalid input or missing file"

def test_parse_resume_invalid_file(client):
    data = {'resume_file': (io.BytesIO(b"not a pdf"), "invalid.txt")}
    response = client.post("/parse_resume", content_type='multipart/form-data', data=data)
    assert response.status_code == 400
    assert response.json["error"] == "Invalid input or missing file"

def test_parse_resume_internal_error(client):
    data = {'resume_file': (io.BytesIO(b'Invalid'), "non_existent.pdf")}
    response = client.post("/parse_resume", content_type='multipart/form-data', data=data)
    assert response.status_code == 500
    assert response.json["error"] == "Internal error while processing the file"

