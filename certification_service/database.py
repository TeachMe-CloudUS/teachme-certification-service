import os
import time
from typing import Optional
from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure, OperationFailure
from certification_service.logger import logger
from datetime import datetime


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
            raise ValueError("Missing required mongodb URI environment variable")
        else:
            logger.info(f"Using MongoDB URI: {mongodb_uri}")

        while retry_count < self.max_retries:
            try:
                if self.client is None:
                    logger.info("Attempting to connect to MongoDB...")
                    self.client = MongoClient(mongodb_uri)
                
                
                # Set up database and collection
                database = os.getenv('MONGO_DATABASE')
                collection_name = os.getenv('MONGO_COLLECTION_NAME')
                if database is None:
                    logger.error("Missing required MONGO_DATABASE environment variable")
                    raise ValueError("Missing required MONGO_DATABASE environment variable")
                else:
                    self.db = self.client[database]

                
                if self.db is None:
                    logger.error(f"Database '{database}' not found")
                    raise ValueError(f"Database '{database}' not found")
                else:
                    logger.info(f"Using database: {database}")
                    self.certificates_collection = self.db[collection_name]
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
                self.client.command('ping')
                return True, "Connected"
            return False, "Client not initialized"
        except Exception as e:
            return False, str(e)

    def store_certificate(self, student, course, blob_link):
        """Store a certificate in MongoDB and return the stored document."""
        if not self._initialized:
            raise ValueError("Database connection not initialized")
        
        certificate_data = {
            'student_id': str(student['id']),
            'name': student['name'],
            'surname': student['surname'],
            'email': student['email'],
            'course_id': str(course['id']),
            'graduation_date': datetime.strptime(student['graduation_date'], "%Y-%m-%d"),
            'blob_link': blob_link
        }
        try:

            result = self.certificates_collection.insert_one(certificate_data)
            
            if not result.acknowledged:
                logger.error(f"Failed to store certificate for student {student['id']} in course {course['id']}")
                return None
            
            return self.certificates_collection.find_one({'_id': result.inserted_id})
        
        except errors.DuplicateKeyError:
            logger.warning(f"Certificate already exists for student {student['id']} in course {course['id']}")
            return None
    
        except Exception as e:
            logger.error(f"Unexpected error storing certificate: {e}")
            raise

    def get_course_cert(self, student_id, course_id):
        """Get certificate for a specific course and student from MongoDB."""
        try:
            # Assuming 'certificates' is the collection name in MongoDB
            certificate = self.certificates_collection.find_one({
                'id': student_id, 
                'courseId': course_id
            })
            
            if certificate:
                return certificate['blob_link']
            else:
                # Log that no certificate was found
                logger.warning(f"No blob link to certificate found for student {student_id} in course {course_id}")
                return None
        
        except Exception as e:
            # Log any database errors
            logger.error(f"Error retrieving blob link certificate for student {student_id} in course {course_id}: {str(e)}")
            raise

    def get_all_course_certs(self, student_id):
        """Retrieve all certificates for a specific student from MongoDB."""
        try:
            # Find all certificates for the given student_id
            certificates = list(self.certificates_collection.find({
                'id': student_id
            }))
            
            if certificates:
                return [cert['blob_link'] for cert in certificates]
            else:
                # Log that no certificates were found
                logger.warning(f"No blob links to certificates found for student {student_id}")
                return []
        
        except Exception as e:
            # Log any database errors
            logger.error(f"Error retrieving blob links to certificates for student {student_id}: {str(e)}")
            raise

    def delete_all_certs(self, student_id):
        """Delete all certificates for a specific student from MongoDB."""
        try:
            # Find certificates for the student
            certificates = list(self.certificates_collection.find({
                'student_id': str(student_id)  # Ensure student_id is converted to string
            }))
            
            # Log found certificates
            logger.info(f"Found {len(certificates)} certificates for student {student_id}")
            
            # Delete all certificates for the student
            result = self.certificates_collection.delete_many({
                'student_id': str(student_id)
            })
            
            # Log deletion result
            logger.info(f"Deleted {result.deleted_count} certificates for student {student_id}")
            
            return result.deleted_count
        
        except Exception as e:
            # Log any database errors with full traceback
            logger.error(f"Error deleting certificates for student {student_id}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise


    mock_student = {
        'id': '69',
        'userId': '069',
        'name': 'Jane',
        'surname': 'Doe',
        'email': 'jane.doe@example.com',
        'courseId': 'Data Science',
        'graduation_date': '2023-06-30'
    }
    mock_course = {
        'id': 'DS101',
        'name': 'Introduction to Data Science',
        'category': 'Technology',
        'description': 'A comprehensive introduction to data science principles and techniques',
        'duration': '12 weeks',
        'completionDate': '2024-06-30',
        'level': 'Beginner'
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
