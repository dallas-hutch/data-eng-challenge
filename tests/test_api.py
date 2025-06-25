import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_sales_daily_valid(client):
    response = client.get("/api/sales/daily?start_date=2024-01-01&end_date=2024-01-10&timezone=UTC")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "summary" in data
    assert data["timezone"] == "UTC"

def test_sales_daily_missing_dates(client):
    response = client.get("/api/sales/daily")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data and "message" in data and data["code"] == 400

def test_sales_daily_invalid_date_format(client):
    response = client.get("/api/sales/daily?start_date=2024-99-01&end_date=2024-01-31")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid date format"

def test_data_quality_endpoint(client):
    response = client.get("/api/data-quality")
    assert response.status_code == 200
    data = response.get_json()
    assert "issues_found" in data
    assert "invalid_dates" in data["issues_found"]

def test_fallback_dst(client):
    response = client.get("/api/sales/hourly?start_date=2024-11-03&end_date=2024-11-03&timezone=America/New_York")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data

def test_404_route(client):
    response = client.get("/api/unknown")
    assert response.status_code == 404