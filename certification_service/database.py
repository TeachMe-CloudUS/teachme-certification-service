import os
import time
from typing import Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from certification_service.logger import logger


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
                self.certificates_collection = self.db.student_certificates
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


    def get_course_cert(self, student_id, course_id):
        """Get certificate for a specific course and student from MongoDB."""
        try:
            # Assuming 'certificates' is the collection name in MongoDB
            certificate = self.certificates_collection.find_one({
                'student_id': student_id, 
                'course_id': course_id
            })
            
            if certificate:
                return {
                    'student_id': certificate['student_id'],
                    'course_id': certificate['course_id'],
                    'certificate_path': certificate['certificate_path'],
                    'created_at': certificate['created_at'],
                    'status': certificate['status']
                }
            else:
                # Log that no certificate was found
                logger.warning(f"No certificate found for student {student_id} in course {course_id}")
                return None
        
        except Exception as e:
            # Log any database errors
            logger.error(f"Error retrieving certificate: {str(e)}")
            raise

    def get_all_course_certs(self, student_id):
        """Retrieve all certificates for a specific student from MongoDB."""
        try:
            # Find all certificates for the given student_id
            certificates = list(self.certificates_collection.find({
                'student_id': student_id
            }))
            
            if certificates:
                # Transform MongoDB documents into a list of certificate details
                formatted_certificates = [{
                    'student_id': cert['student_id'],
                    'course_id': cert['course_id'],
                    'certificate_path': cert['certificate_path'],
                    'created_at': cert['created_at'],
                    'status': cert['status']
                } for cert in certificates]
                
                return formatted_certificates
            else:
                # Log that no certificates were found
                logger.warning(f"No certificates found for student {student_id}")
                return []
        
        except Exception as e:
            # Log any database errors
            logger.error(f"Error retrieving certificates for student {student_id}: {str(e)}")
            raise

    def delete_all_certs(self, student_id):
        """Delete all certificates for a specific student from MongoDB."""
        try:
            # Delete all certificates from the database
            delete_result = self.certificates_collection.delete_many({
                'student_id': student_id
            })
            
            # Log the deletion
            if delete_result.deleted_count > 0:
                logger.info(f"Deleted {delete_result.deleted_count} certificates for student {student_id}")
            else:
                logger.warning(f"No certificates found to delete for student {student_id}")
            
            return delete_result.deleted_count
        
        except Exception as e:
            # Log any database errors
            logger.error(f"Error deleting certificates for student {student_id}: {str(e)}")
            raise

# Function to get mock student data
def get_mock_student_data(student_id):
    """Retrieve mock data for a student given their student ID."""
    return {
        'id': student_id,
        'name': 'Jane Doe',
        'email': 'jane.doe@example.com',
        'courseId': 'Data Science',
        'graduation_date': '2023-06-30'
    }

# Function to get mock course data 
def get_mock_course_data(course_id):
    """Retrieve mock data for a course given its course ID."""
    return {
        'id': course_id,
        'name': 'Data Science',
        'description': 'xyz',
        'duration': '12 weeks',
        'start_date': '2023-03-15'
    }

# Create a global instance
db_connection = DatabaseConnection()
