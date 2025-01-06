import pytest
from certification_service.database import DatabaseConnection
from certification_service.models.student_course_data import Student_Course_Data

@pytest.fixture(scope="function")
def clean_database():
    """
    Fixture to ensure a clean database state before each test.
    
    Scope is 'function' to reset database for each individual test.
    This prevents tests from interfering with each other.
    """
    # Create a database connection
    db_connection = DatabaseConnection()
    
    try:
        # Drop the entire collection before the test
        db_connection.certificates_collection.drop()
        
        # Yield the database connection so tests can use it
        yield db_connection
    
    finally:
        # Optional: Drop the collection again after the test to ensure cleanup
        db_connection.certificates_collection.drop()
        
        # Close the database connection
        db_connection.close()

def create_test_student_course_data(student_id=None, course_id=None):
    """
    Create a test Student_Course_Data instance.
    
    Args:
        student_id (str, optional): Custom student ID
        course_id (str, optional): Custom course ID
    
    Returns:
        Student_Course_Data: A test data instance
    """
    return Student_Course_Data(
        student_id=student_id or "test_student_123",
        student_userId="test_user_456",
        student_name="Test",
        student_surname="Student",
        student_email="test.student@example.com",
        course_id=course_id or "test_course_789",
        course_name="Test Course",
        course_description="A test course description",
        course_duration="6 months",
        course_level="Intermediate",
        completionDate="2025-01-05"
    )

def test_database_connection(clean_database):
    """Test establishing a database connection."""
    db_connection = clean_database
    assert db_connection.certificates_collection is not None, "Failed to establish database connection"

def test_store_certificate(clean_database):
    """Test storing a certificate in the database."""
    db_connection = clean_database
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/test-certificate.pdf'
    
    # Store certificate
    stored_cert = db_connection.store_certificate(student_course_data, blob_url)
    
    assert stored_cert is not None, "Failed to store certificate"
    assert stored_cert['student_id'] == student_course_data.student_id
    assert stored_cert['course_id'] == student_course_data.course_id
    assert stored_cert['blob_link'] == blob_url

def test_duplicate_certificate_prevention(clean_database):
    """Test that duplicate certificates are prevented and existing certificates are retrieved."""
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/first_test-certificate.pdf'
    
    # First certificate storage should succeed
    first_cert = clean_database.store_certificate(student_course_data, blob_url)
    assert first_cert is not None, "First certificate storage failed"
    
    # Second certificate with same student and course should return the existing certificate
    second_cert = clean_database.store_certificate(student_course_data, blob_url)
    assert second_cert is not None, "Second certificate retrieval failed"
    
    # Verify that the certificates are the same
    assert first_cert['blob_link'] == second_cert['blob_link'], "Retrieved certificate does not match original"
    
    # Try to insert a certificate with the same student_id and course_id but different blob_url
    second_blob_url = 'https://example.com/second_test-certificate.pdf'
    third_cert = clean_database.store_certificate(student_course_data, second_blob_url)
    
    # This should still return the original certificate
    assert third_cert['blob_link'] == first_cert['blob_link'], "If an certificate exists already for this course and student "
    f"it is returned even if the blob link of the inserted certificate is different from the existing one"
    
    # Verify only one certificate exists in the database
    certificate_count = clean_database.certificates_collection.count_documents({
        'student_id': student_course_data.student_id,
        'course_id': student_course_data.course_id
    })
    assert certificate_count == 1, "Multiple certificates created for same student and course"

def test_mongodb_connection_and_collection(clean_database):
    """Comprehensive test of MongoDB connection and collection."""
    db_connection = clean_database
    
    # Verify collection exists
    assert db_connection.certificates_collection is not None, "Certificates collection not found"
    
    # Verify initial collection is empty
    initial_count = db_connection.certificates_collection.count_documents({})
    assert initial_count == 0, f"Collection should be empty, but contains {initial_count} documents"

def test_delete_certificate(clean_database):
    """Test deleting a certificate."""
    db_connection = clean_database
    
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/test-certificate.pdf'
    
    # Store certificate first
    db_connection.store_certificate(student_course_data, blob_url)
    
    # Delete certificate
    deleted = db_connection.delete_certificate(
        student_course_data.student_id, 
        student_course_data.course_id
    )
    
    assert deleted, "Certificate deletion failed"
    
    # Verify the certificate is no longer in the database
    retrieved_cert = db_connection.get_course_cert(
        student_course_data.student_id, 
        student_course_data.course_id
    )
    assert retrieved_cert is None, "Certificate was not deleted from the database"

def test_retrieve_certificate(clean_database):
    """Test retrieving a specific certificate."""
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/test-certificate.pdf'
    
    # Store certificate
    clean_database.store_certificate(student_course_data, blob_url)
    
    # Retrieve certificate blob link
    retrieved_blob_link = clean_database.get_course_cert(
        student_course_data.student_id, 
        student_course_data.course_id
    )
    
    assert retrieved_blob_link is not None, "Failed to retrieve certificate blob link"
    assert retrieved_blob_link == blob_url, "Retrieved blob link does not match stored blob link"

def test_delete_all_certs(clean_database):
    """Test deleting all certificates for a student."""
    db_connection = clean_database
    
    # Create multiple certificates for the same student
    student_id = "test_student_1"
    certificates_data = [
        create_test_student_course_data(student_id=student_id, course_id="course1"),
        create_test_student_course_data(student_id=student_id, course_id="course2"),
        create_test_student_course_data(student_id=student_id, course_id="course3")
    ]
    
    # Store multiple certificates
    for cert_data in certificates_data:
        db_connection.store_certificate(cert_data, f'https://example.com/{cert_data.course_id}-certificate.pdf')
    
    # Delete all certificates for the student
    db_connection.delete_all_certs(student_id)
    
    # Verify no certificates remain for the student
    remaining_certs = db_connection.get_all_course_certs(student_id)
    assert len(remaining_certs) == 0, "Not all certificates were deleted"
