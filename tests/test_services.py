import pytest
from unittest.mock import patch
import os
import sys
import requests

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock student data
mock_student_data = {
    'id': 1,
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'course_id': 'CS101',
    'course_name': 'Computer Science',
    'graduation_date': '2023-06-30'
}

@patch('requests.post')
def test_certification_service(mock_post):
    # Mock the response of the certification service
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        'certificate_path': f"certificates/certificate_{mock_student_data['id']}.pdf"
    }

    response = requests.post('http://localhost:5002/certify/1')
    assert response.status_code == 200
    assert 'certificate_path' in response.json()
    assert os.path.exists(response.json()['certificate_path'])

