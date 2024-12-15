import os
import pytest
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

def get_mongodb_client(uri_var='MONGODB_URI_USER'):
    """Create and return a MongoDB client using connection string from environment variables."""
    try:
        # Use the MongoDB URI from environment variables
        connection_string = os.getenv(uri_var)
        
        # Create client with connection timeouts
        client = MongoClient(
            connection_string, 
            connectTimeoutMS=5000,  # 5 seconds connection timeout
            serverSelectionTimeoutMS=5000  # 5 seconds server selection timeout
        )
        
        # Verify connection by checking server info
        client.server_info()
        
        return client
    except Exception as e:
        pytest.fail(f"MongoDB connection failed for {uri_var}: {e}")

        
def test_user_database_connection():
    """Test connection using user credentials."""
    client = get_mongodb_client('MONGODB_URI_USER')
    
    try:
        # Verify basic database access
        databases = client.list_database_names()
        assert os.getenv('MONGO_DATABASE') in databases, "Expected database not found"
    finally:
        client.close()

def test_admin_database_connection():
    """Test connection using admin credentials."""
    client = get_mongodb_client('MONGODB_URI_ADMIN')
    
    try:
        # Verify admin can list all databases
        databases = client.list_database_names()
        assert len(databases) > 0, "Admin should be able to list databases"
    finally:
        client.close()

def test_certificates_collection():
    """Verify certificates collection exists and can be accessed."""
    client = get_mongodb_client('MONGODB_URI_USER')
    
    try:
        db = client[os.getenv('MONGO_DATABASE')]
        collection = db[os.getenv('MONGO_COLLECTION_NAME', 'student_certificates')]
        
        # Perform a simple operation to verify collection access
        collection.count_documents({})
    except Exception as e:
        pytest.fail(f"Collection access failed: {e}")
    finally:
        client.close()