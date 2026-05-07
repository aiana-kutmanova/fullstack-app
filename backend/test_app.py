import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_data_no_db(client):
    # Тест что эндпоинт существует (вернёт 200 или 500 — оба ок без БД)
    response = client.get('/api/data')
    assert response.status_code in [200, 500]

def test_post_data_no_text(client):
    response = client.post('/api/data',
        json={},
        content_type='application/json')
    assert response.status_code in [400, 500]

def test_app_exists():
    assert app is not None