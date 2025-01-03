import os
import pytest
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from datetime import datetime
from certification_service.database import DatabaseConnection
from certification_service.models.student_course_data import Student_Course_Data

load_dotenv()

def get_mongodb_client(uri_var='MONGODB_URI_USER'):
    """Create and return a MongoDB client using connection string from environment variables."""
    try:
        connection_string = os.getenv(uri_var)
        
        client = MongoClient(
            connection_string, 
            connectTimeoutMS=5000,  
            serverSelectionTimeoutMS=5000  
        )
        
        client.server_info()
        return client
    except Exception as e:
        pytest.fail(f"MongoDB connection failed for {uri_var}: {e}")

def create_test_student_course_data():
    """Create a sample Student_Course_Data instance for testing."""
    return Student_Course_Data(
        student_id='test_student_123',
        student_userId='test_user_456',
        student_name='John',
        student_surname='Doe',
        student_email='john.doe@example.com',
        course_id='test_course_789',
        course_name='Test Course',
        course_description='A comprehensive test course',
        course_duration='12 weeks',
        course_level='Intermediate',
        completionDate='2024-01-03T12:00:00Z'
    )

def test_database_connection():
    """Test database connection and initialization."""
    db_connection = DatabaseConnection()
    assert db_connection._initialized, "Database connection should be initialized"

def test_store_certificate():
    """Test storing a certificate."""
    db_connection = DatabaseConnection()
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/test-certificate.pdf'
    
    # Store certificate
    stored_cert = db_connection.store_certificate(student_course_data, blob_url)
    
    assert stored_cert is not None, "Certificate should be stored successfully"
    assert stored_cert['student_id'] == student_course_data.student_id, "Stored student ID should match"
    assert stored_cert['blob_link'] == blob_url, "Blob URL should be stored correctly"

def test_retrieve_certificate():
    """Test retrieving a specific certificate."""
    db_connection = DatabaseConnection()
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/test-certificate.pdf'
    
    # Store certificate first
    db_connection.store_certificate(student_course_data, blob_url)
    
    # Retrieve certificate
    retrieved_cert = db_connection.get_certificate_by_student_and_course(
        student_course_data.student_id, 
        student_course_data.course_id
    )
    
    assert retrieved_cert is not None, "Certificate should be retrievable"
    assert retrieved_cert['student_name'] == student_course_data.student_name, "Retrieved student name should match"

def test_duplicate_certificate_prevention():
    """Test that duplicate certificates are prevented."""
    db_connection = DatabaseConnection()
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/test-certificate.pdf'
    
    # First storage should succeed
    first_store = db_connection.store_certificate(student_course_data, blob_url)
    assert first_store is not None, "First certificate storage should succeed"
    
    # Second storage should fail (duplicate)
    second_store = db_connection.store_certificate(student_course_data, blob_url)
    assert second_store is None, "Second certificate storage should fail due to duplicate"

def test_delete_certificate():
    """Test deleting a certificate."""
    db_connection = DatabaseConnection()
    student_course_data = create_test_student_course_data()
    blob_url = 'https://example.com/test-certificate.pdf'
    
    # Store certificate first
    db_connection.store_certificate(student_course_data, blob_url)
    
    # Delete certificate
    deleted, message = db_connection.delete_certificate(
        student_course_data.student_id, 
        student_course_data.course_id
    )
    
    assert deleted, f"Certificate deletion failed: {message}"

def test_mongodb_connection_and_collection():
    """Comprehensive test of MongoDB connection and collection."""
    client = get_mongodb_client('MONGODB_URI_USER')
    
    try:
        # Verify database exists
        db_name = os.getenv('MONGO_DATABASE')
        assert db_name in client.list_database_names(), "Expected database not found"
        
        # Verify collection exists
        db = client[db_name]
        collection_name = os.getenv('MONGO_COLLECTION_NAME', 'student_certificates')
        assert collection_name in db.list_collection_names(), "Expected collection not found"
        
        # Verify collection can be accessed
        collection = db[collection_name]
        collection.count_documents({})
    except Exception as e:
        pytest.fail(f"MongoDB collection access failed: {e}")
    finally:
        client.close()