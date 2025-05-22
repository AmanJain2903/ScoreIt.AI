import io
import pytest
from api.app import create_app

pytestmark = pytest.mark.api

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()

def test_success(client):
    response = client.get('/get_model_config')
    assert response.status_code == 200
    assert len(response.json) > 0

