import requests
import pytest

BASE_URL = "http://certification-service:8080/api/v1"

# Constants for frequently used student_id and course_id
VALID_STUDENT_ID = 1
VALID_COURSE_ID = 101
INVALID_STUDENT_ID = 9999
INVALID_COURSE_ID = 9999

# Helper function for error checking (checks failure cases)
def check_failure(response, status_code):
    """Checks for failure and ensures the response has the correct error status."""
    assert response.status_code == status_code
    assert "success" not in response.json()

# Test for POST /certify/<student_id>/<course_id> route
def test_certify_student():
    # Test for valid student_id and course_id
    response = requests.post(f"{BASE_URL}/certify/{VALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 200
    assert response.json() == {"success": True}

    # Test for invalid student_id
    response = requests.post(f"{BASE_URL}/certify/{INVALID_STUDENT_ID}/{VALID_COURSE_ID}")
    check_failure(response, 400)

    # Test for invalid course_id
    response = requests.post(f"{BASE_URL}/certify/{VALID_STUDENT_ID}/{INVALID_COURSE_ID}")
    check_failure(response, 400)

# Test for POST /certify route with JSON data
def test_certify():
    payload = {
        "student_id": VALID_STUDENT_ID,
        "course_id": VALID_COURSE_ID
    }
    # Test for valid data
    response = requests.post(f"{BASE_URL}/certify", json=payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}

    # Test for missing course_id in the payload
    payload_invalid = {
        "student_id": VALID_STUDENT_ID
    }
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    assert response.status_code == 400
    assert "Error" in response.json()

    # Test for missing student_id and course_id in the payload
    payload_invalid = {}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    assert response.status_code == 400
    assert "Error" in response.json()

    # Test for invalid student_id in the payload
    payload["student_id"] = INVALID_STUDENT_ID
    response = requests.post(f"{BASE_URL}/certify", json=payload)
    check_failure(response, 400)

    # Test for invalid course_id in the payload
    payload["course_id"] = INVALID_COURSE_ID
    response = requests.post(f"{BASE_URL}/certify", json=payload)
    check_failure(response, 400)

# Test for GET /certificates/<student_id> route (Get all certificates for a student)
def test_get_all_certificates():
    # Test for valid student_id
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Expecting a list of certificates

    # Test for invalid student_id
    response = requests.get(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

# Test for GET /certificates/<student_id>/<course_id> route (Get specific course certificate for a student)
def test_get_course_certificate():
    # Test for valid student_id and course_id
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)  # Expecting a single certificate object

    # Test for invalid student_id
    response = requests.get(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

    # Test for invalid course_id
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}/{INVALID_COURSE_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

# Test for DELETE /certificates/<student_id> route (Delete all certificates for a student)
def test_delete_student_certificates():
    # Test for valid student_id
    response = requests.delete(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}")
    assert response.status_code == 200
    assert "Deleted" in response.json()["message"]

    # Test for invalid student_id
    response = requests.delete(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

    # Test for handling exception (simulate internal server error e.g. database error)
    response = requests.delete(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 500
    assert "error" in response.json()
