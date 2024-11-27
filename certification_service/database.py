import os
import time
import urllib.parse
from logger import logger
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


class DatabaseConnection:
    def __init__(self, max_retries: int = 5, retry_delay: int = 5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client: Optional[MongoClient] = None
        self.db = None
        self.certificates_collection = None
        self._initialized = False

    def init_mongodb(self):
        """Initialize MongoDB connection with retry logic."""
        retry_count = 0
        last_exception = None

        mongodb_uri = os.getenv('MONGODB_URI_USER')
        if not mongodb_uri:
            raise ValueError("Missing required MONGODB_URI_ADMIN environment variable")
        else:
            logger.info(f"Using MongoDB URI: {mongodb_uri}")

        while retry_count < self.max_retries:
            try:
                if self.client is None:
                    logger.info("Attempting to connect to MongoDB...")
                    self.client = MongoClient(mongodb_uri)
                
                # Test the connection
                self.client.admin.command('ping')
                
                # Set up database and collection
                database = os.getenv('MONGO_DATABASE', 'certificate_db')
                self.db = self.client[database]
                self.certificates_collection = self.db.certificates
                self._initialized = True
                
                logger.info("Successfully connected to MongoDB")
                return self.client

            except (ConnectionFailure, OperationFailure) as e:
                last_exception = e
                retry_count += 1
                wait_time = self.retry_delay * retry_count
                
                logger.warning(
                    f"Failed to connect to MongoDB (attempt {retry_count}/{self.max_retries}). "
                    f"Retrying in {wait_time} seconds... Error: {str(e)}"
                )
                
                time.sleep(wait_time)

        error_msg = f"Failed to connect to MongoDB after {self.max_retries} attempts"
        logger.error(error_msg)
        raise last_exception

    def get_client(self) -> MongoClient:
        """Get MongoDB client, creating it if necessary."""
        if not self._initialized:
            self.init_mongodb()
        return self.client

    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self._initialized = False

    def check_connection(self):
        """Check if the MongoDB connection is healthy."""
        try:
            if self.client is not None:
                self.client.admin.command('ping')
                return True, "Connected"
            return False, "Client not initialized"
        except Exception as e:
            return False, str(e)

    def store_certificate(self, certificate_data):
        """Store a certificate in MongoDB and return the stored document."""
        if not self._initialized:
            raise ValueError("Database connection not initialized")
        result = self.certificates_collection.insert_one(certificate_data)
        return self.certificates_collection.find_one({'_id': result.inserted_id})


# Function to get mock student data
def get_mock_student_data(student_id):
    """Retrieve mock data for a student given their student ID."""
    return {
        'id': student_id,
        'name': 'Jane Doe',
        'email': 'jane.doe@example.com',
        'course': 'Data Science',
        'graduation_date': '2023-06-30'
    }

# Create a global instance
db_connection = DatabaseConnection()
