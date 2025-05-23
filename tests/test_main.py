from fastapi.testclient import TestClient
import pytest # TestClient is often used with pytest
import os
import sys

# Add the project root to the Python path to allow main to be imported
# This assumes tests/ is one level down from the project root where main.py is
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app # Import the FastAPI application from main.py

client = TestClient(app)

def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    response_index = client.get("/index")
    assert response_index.status_code == 200
    assert "text/html" in response_index.headers["content-type"]

def test_get_points_valid_payload():
    # A valid GeoJSON polygon coordinate structure (closed linear ring with 4+ points)
    # Min 3 unique points, first and last are the same.
    valid_bounding_box = {
        "coordinates": [
            [0, 0], [0, 10], [10, 10], [10, 0], [0, 0]
        ]
    }
    response = client.post("/getpoints", json=valid_bounding_box)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["type"] == "FeatureCollection"
    assert "features" in response_json
    assert isinstance(response_json["features"], list)

def test_get_points_invalid_payload_not_closed():
    # Invalid: Polygon not closed
    invalid_bounding_box = {
        "coordinates": [
            [0, 0], [0, 10], [10, 10], [10, 0] # Not closed
        ]
    }
    response = client.post("/getpoints", json=invalid_bounding_box)
    assert response.status_code == 422 # Expecting Pydantic validation error

def test_get_points_invalid_payload_too_few_points():
    # Invalid: Polygon too few points
    invalid_bounding_box = {
        "coordinates": [
            [0, 0], [0, 10], [0, 0] # Only 2 unique points
        ]
    }
    response = client.post("/getpoints", json=invalid_bounding_box)
    assert response.status_code == 422

def test_get_points_invalid_payload_wrong_format():
    # Invalid: Data format incorrect (e.g. not a list of lists)
    invalid_bounding_box = {
        "coordinates": "not a list"
    }
    response = client.post("/getpoints", json=invalid_bounding_box)
    assert response.status_code == 422

def test_request_help_form_display():
    response = client.get("/requesthelp")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_offer_help_form_display():
    response = client.get("/offerhelp")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

# Placeholder for more tests (uploadrequest, uploadoffer, showinfo)
# These might require mocking the database or more setup if we don't want them
# to interact with a live DB during tests.
# For now, we'll focus on endpoint availability and basic validation.

# (Keep existing imports and TestClient instance: client)
# from bson import ObjectId # Might be needed if we construct valid ObjectIds for testing found cases

# --- Tests for /uploadrequest ---

def test_upload_request_valid_data():
    # For these tests, we are hitting the actual DB if not mocked.
    # A successful submission returns "1" as plain text.
    form_data = {
        "name": "Test User",
        "phone": "1234567890",
        "address": "123 Test St",
        "email": "test@example.com",
        "noofpeople": "2",
        "request_service": "Food", # Must be one of SERVICES_LIST and not "Select"
        "notes": "Test notes for request",
        "lat": "13.0",
        "lng": "80.0"
    }
    response = client.post("/uploadrequest", data=form_data)
    assert response.status_code == 200
    assert response.text == "1"
    # To make this test more robust in a real scenario, you might query the DB
    # to confirm the entry, or use a dedicated test DB and cleanup.

def test_upload_request_invalid_data_missing_required():
    form_data = {
        "name": "Test User",
        # "phone": "1234567890", # Missing phone
        "request_service": "Food",
        "lat": "13.0",
        "lng": "80.0"
    }
    response = client.post("/uploadrequest", data=form_data)
    assert response.status_code == 422 # Pydantic validation error
    response_json = response.json()
    assert any(err["loc"] == ["body", "phone"] for err in response_json["detail"])

def test_upload_request_invalid_service():
    form_data = {
        "name": "Test User",
        "phone": "1234567890",
        "request_service": "InvalidService", # Not in SERVICES_LIST
        "lat": "13.0",
        "lng": "80.0"
    }
    response = client.post("/uploadrequest", data=form_data)
    assert response.status_code == 422
    response_json = response.json()
    assert any(err["loc"] == ["body", "request_service"] for err in response_json["detail"])

# --- Tests for /uploadoffer ---

def test_upload_offer_valid_data():
    form_data = {
        "name": "Test Helper",
        "phone": "0987654321",
        "address": "456 Helper Ave",
        "email": "helper@example.com",
        "noofpeople": "1",
        "offer_service": "Shelter", # Must be one of SERVICES_LIST and not "Select"
        "notes": "Test notes for offer",
        "lat": "13.1",
        "lng": "80.1"
    }
    response = client.post("/uploadoffer", data=form_data)
    assert response.status_code == 200
    assert response.text == "1"

def test_upload_offer_invalid_data_missing_required():
    form_data = {
        "name": "Test Helper",
        # "phone": "0987654321", # Missing phone
        "offer_service": "Shelter",
        "lat": "13.1",
        "lng": "80.1"
    }
    response = client.post("/uploadoffer", data=form_data)
    assert response.status_code == 422
    response_json = response.json()
    assert any(err["loc"] == ["body", "phone"] for err in response_json["detail"])

def test_upload_offer_invalid_service():
    form_data = {
        "name": "Test Helper",
        "phone": "0987654321",
        "offer_service": "Select", # "Select" is invalid as per Pydantic validator
        "lat": "13.1",
        "lng": "80.1"
    }
    response = client.post("/uploadoffer", data=form_data)
    assert response.status_code == 422
    response_json = response.json()
    assert any(err["loc"] == ["body", "offer_service"] for err in response_json["detail"])


# --- Tests for /showinfo ---

def test_show_info_invalid_id_format():
    response = client.get("/showinfo?id=invalid-object-id-format")
    assert response.status_code == 400 # Invalid ObjectId format
    response_json = response.json()
    assert "Invalid ID format" in response_json["detail"]


def test_show_info_non_existent_id():
    # This is a valid ObjectId format but unlikely to exist.
    # If your DB is empty, this should reliably give 404.
    # If running tests against a populated DB, pick an ID known not to exist.
    non_existent_id = "60c72b9f9b1e8b001f8e4d1a" # Example valid format ObjectId
    response = client.get(f"/showinfo?id={non_existent_id}")
    assert response.status_code == 404
    response_json = response.json()
    assert "Information not found" in response_json["detail"]

def test_show_info_missing_id():
    response = client.get("/showinfo") # No id query parameter
    # FastAPI should catch this as a missing required query parameter if 'id: str'
    # If 'id: Optional[str] = None', then our route logic for 'if not id:' handles it.
    # Based on current main.py, 'id: str' is required.
    # FastAPI gives 422 if a path/query param is missing and not Optional.
    assert response.status_code == 422 # Or 400 if handled manually before Pydantic
    # The current main.py has 'id: str', so FastAPI's validation should yield 422
    # if the query parameter 'id' is not provided.
    # If the route was (id: Optional[str] = Query(None)), then our manual check
    # "if not id: raise HTTPException(status_code=400..." would be hit.
    # Let's verify what main.py has for showinfo: `async def show_info(request: Request, id: str):`
    # This means 'id' is a required query parameter.
    response_json = response.json()
    assert any(err["type"] == "missing" and err["loc"] == ["query", "id"] for err in response_json["detail"])
