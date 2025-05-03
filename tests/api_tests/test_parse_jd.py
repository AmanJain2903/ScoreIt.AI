import io
import pytest
from api.app import create_app

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_parse_jd_valid_link(client):
    data = {'jd_link': 'https://www.linkedin.com/jobs/view/4002614315'}
    response = client.post("/parse_jd", content_type='multipart/form-data', data=data)
    assert response.status_code == 200
    assert "jd_text" in response.json

def test_parse_jd_no_input(client):
    data = {'jd_link': None}
    response = client.post("/parse_jd", content_type='multipart/form-data', data=data)
    assert response.status_code == 400
    assert response.json["error"] == "Invalid input or missing link"

def test_parse_jd_invalid_link(client):
    data = {'jd_link': 1234}
    response = client.post("/parse_jd", content_type='multipart/form-data', data=data)
    assert response.status_code == 400
    assert response.json["error"] == "Invalid input or missing link"

def test_parse_jd_internal_error(client):
    data = {'jd_link': 'https://www.MOCKLINKEDIN.com/jobs/view/InvalidJob'}
    response = client.post("/parse_jd", content_type='multipart/form-data', data=data)
    assert response.status_code == 500
    assert response.json["error"] == "Internal error while processing the link"

