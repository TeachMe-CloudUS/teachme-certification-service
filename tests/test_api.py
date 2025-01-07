import requests
import pytest
import re

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
VALID_COMPLETION_DATE = "2025-01-04T13:24:11Z"

INVALID_STUDENT_ID = ""
INVALID_COURSE_ID = ""
INVALID_STUDENT_EMAIL = ""

# Helper function for failure checking
def check_failure(response, status_code):
    """Checks for failure and ensures the response has the correct error status."""
    assert response.status_code == status_code
    assert "success" not in response.json()

# Common payload for tests
BASE_PAYLOAD = {
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

# Test for POST /certify 
def test_certify_valid_data():
    response = requests.post(f"{BASE_URL}/certify", json=BASE_PAYLOAD)
    assert response.status_code == 201
    assert isinstance(response.json()['success'], str) and response.json()['success'].startswith('http')

def test_certify_invalid_student_id():
    payload_invalid = {**BASE_PAYLOAD, "student_id": INVALID_STUDENT_ID}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

def test_certify_invalid_student_userId():
    payload_invalid = {**BASE_PAYLOAD, "student_userId": ""}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

def test_certify_invalid_student_email():
    payload_invalid = {**BASE_PAYLOAD, "student_email": INVALID_STUDENT_EMAIL}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

def test_certify_invalid_course_id():
    payload_invalid = {**BASE_PAYLOAD, "course_id": INVALID_COURSE_ID}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

def test_certify_invalid_completion_date():
    payload_invalid = {**BASE_PAYLOAD, "completionDate": ""}
    response = requests.post(f"{BASE_URL}/certify", json=payload_invalid)
    check_failure(response, 400)

# Test for GET all certificates for a student
def test_get_all_certificates_valid():
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_all_certificates_invalid():
    response = requests.get(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 404
    try:
        response_data = response.json()
    except requests.exceptions.JSONDecodeError:
        response_data = {}
    assert response_data == {}

# Test for GET specific course certificate for a student
def test_get_course_certificate_valid():
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 200
    certificate_url = response.text.strip()
    assert isinstance(certificate_url, str)
    assert re.match(r'^"http.*\.pdf"$', certificate_url)

def test_get_course_certificate_invalid_student():
    response = requests.get(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 404
    error_message = response.json().get("message")
    assert error_message.startswith("No certificates found for this student."), f"Unexpected error message: {error_message}"

def test_get_course_certificate_invalid_course():
    response = requests.get(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}/{INVALID_COURSE_ID}")
    assert response.status_code == 404
    

# Test for DELETE all certificates for a student
def test_delete_student_certificates_valid():
    response = requests.delete(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}")
    assert response.status_code == 200

def test_delete_student_certificates_invalid():
    requests.post(f"{BASE_URL}/certify", json=BASE_PAYLOAD)
    response = requests.delete(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}")
    assert response.status_code == 404
    assert response.json().get("error").startswith("Failed to delete certificate")

# Test for DELETE certificate for a student and course
def test_delete_student_certificate_valid():
    requests.post(f"{BASE_URL}/certify", json=BASE_PAYLOAD) 
    response = requests.delete(f"{BASE_URL}/certificate/{VALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 200
    assert "Certificate deleted successfully for" in response.json().get("message", "")
    
def test_delete_student_certificate_invalidStudentID():
    requests.post(f"{BASE_URL}/certify", json=BASE_PAYLOAD)
    response = requests.delete(f"{BASE_URL}/certificates/{INVALID_STUDENT_ID}/{VALID_COURSE_ID}")
    assert response.status_code == 404  

def test_delete_student_certificate_invalidCourseID(): 
    requests.post(f"{BASE_URL}/certify", json=BASE_PAYLOAD)
    response = requests.delete(f"{BASE_URL}/certificates/{VALID_STUDENT_ID}/{INVALID_COURSE_ID}")
    assert response.status_code == 404 

def test_delete_student_certificate_noContent():
    response = requests.delete(f"{BASE_URL}/certificates/{9999}/{9999}")
    assert response.status_code == 404
    
# Test for PUT /certificates/{student_id}/{course_id}
def test_update_certificate_valid():
    requests.post(f"{BASE_URL}/certify", json=BASE_PAYLOAD)
    response = requests.put(f"{BASE_URL}/certificate/{VALID_STUDENT_ID}/{VALID_COURSE_ID}", 
    json={**BASE_PAYLOAD, "student_surname": "Müller"})
    assert response.status_code == 200

def test_update_certificate_invalidStudent():
    response = requests.put(f"{BASE_URL}/certificate/{INVALID_STUDENT_ID}/{VALID_COURSE_ID}", json=BASE_PAYLOAD)
    assert response.status_code == 404 

def test_update_certificate_invalidCourse():
    response = requests.put(f"{BASE_URL}/certificate/{VALID_STUDENT_ID}/{INVALID_COURSE_ID}", json=BASE_PAYLOAD)
    assert response.status_code == 404