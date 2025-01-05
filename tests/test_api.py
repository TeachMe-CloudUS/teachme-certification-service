import requests
import pytest

BASE_URL = "http://certification_service:8080/api/v1"

VALID_STUDENT_ID = "1"
VALID_COURSE_ID = "101"
VALID_STUDENT_USER_ID = "12345"
VALID_STUDENT_NAME = "John"
VALID_STUDENT_SURNAME = "Doe"
VALID_STUDENT_EMAIL = "john.doe@example.com"
VALID_COURSE_NAME = "Python Programming"
VALID_COURSE_DESCRIPTION = "A comprehensive Python course"
VALID_COURSE_DURATION = "6 months"
VALID_COURSE_LEVEL = "Intermediate"
VALID_COMPLETION_DATE = "2025-01-01"

INVALID_STUDENT_ID = "9999"
INVALID_COURSE_ID = "9999"
INVALID_STUDENT_EMAIL = "invalid_email"

# Helper function for failure checking
def check_failure(response, status_code):
    """Checks for failure and ensures the response has the correct error status."""
    assert response.status_code == status_code
    assert "success" not in response.json()

# Test for POST /certify 
def test_certify():
    payload = {
        "student_id": VALID_STUDENT_ID,
        "student_userId": VALID_STUDENT_USER_ID,
        "student_name": VALID_STUDENT_NAME,
        "student_surname": VALID_STUDENT_SURNAME,
        "student_email": VALID_STUDENT_EMAIL,
        "course_id": VALID_COURSE_ID,
        "course_name": VALID_COURSE_NAME,
        "course_description": VALID_COURSE_DESCRIPTION,
        "course_duration": VALID_COURSE_DURATION,
        "course_level": VALID_COURSE_LEVEL,
        "completionDate": VALID_COMPLETION_DATE
    }
    
    # Test for valid data (all fields are correct)
    response = requests.post(f"{BASE_URL}/certify", json=payload)
    assert response.status_code == 200
    assert response.json() == {"success": True}

    # Test for invalid student_id 
    payload_invalid = {**payload, "student_id": INVALID_STUDENT_ID}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

    # Test for invalid student_userId (
    payload_invalid = {**payload, "student_userId": "invalid_user_id"}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

    # Test for invalid student_email
    payload_invalid = {**payload, "student_email": INVALID_STUDENT_EMAIL}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

    # Test for invalid course_id 
    payload_invalid = {**payload, "course_id": INVALID_COURSE_ID}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

    # Test for invalid course_name 
    payload_invalid = {**payload, "course_name": ""}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

    # Test for invalid completionDate 
    payload_invalid = {**payload, "completionDate": "invalid_date"}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

# Test for GET all certificates for a student
def test_get_all_certificates():
    # Test for valid student_id
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  

    # Test for invalid student_id
    response = requests.get(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

# Test for GET specific course certificate for a student
def test_get_course_certificate():
    # Test for valid student_id and course_id
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 200
    assert isinstance(response.json(), dict) 

    # Test for invalid student_id
    response = requests.get(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

    # Test for invalid course_id
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}/{INVALID_COURSE_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

# Test for DELETEall certificates for a student
def test_delete_student_certificates():
    # Test for valid student_id
    response = requests.delete(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}")
    assert response.status_code == 200
    assert "Deleted" in response.json()["message"]

    # Test for invalid student_id
    response = requests.delete(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 404
    assert "message" in response.json()

    # Test for error handling (simulate internal server error, e.g., database error)
    response = requests.delete(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 500
    assert "error" in response.json()
