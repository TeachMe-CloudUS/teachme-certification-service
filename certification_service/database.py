import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import urllib.parse

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.client = None
        self.db = None
        self.certificates_collection = None
        self._initialized = False

    def init_mongodb(self):
        """Initialize MongoDB connection with error handling."""
        try:
            # Get connection parameters from environment
            username = os.getenv('MONGO_USERNAME')
            password = os.getenv('MONGO_PASSWORD')
            database = os.getenv('MONGO_DATABASE', 'certificate_db')
            
            if not all([username, password]):
                raise ValueError("Missing required MongoDB credentials")
            
            # URL encode username and password
            username = urllib.parse.quote_plus(username)
            password = urllib.parse.quote_plus(password)
            
            # Construct MongoDB URI
            mongodb_uri = f"mongodb://{username}:{password}@mongodb:27017/{database}?authSource=admin"
            
            logger.info("Attempting to connect to MongoDB...")
            self.client = MongoClient(mongodb_uri)
            
            # Force a connection attempt by running a command
            self.client.admin.command('ping')
            
            # Set up database and collection
            self.db = self.client[database]
            self.certificates_collection = self.db.certificates
            self._initialized = True
            
            logger.info("Successfully connected to MongoDB")
            return self.client
        except ConnectionFailure as e:
            error_msg = f"Failed to connect to MongoDB: {str(e)}"
            logger.error(error_msg)
            raise ConnectionFailure(error_msg)
        except OperationFailure as e:
            error_msg = f"Authentication failed: {str(e)}"
            logger.error(error_msg)
            # Log additional connection details (without sensitive info)
            mongo_user = os.getenv('MONGO_USERNAME', 'not_set')
            mongo_db = os.getenv('MONGO_DATABASE', 'not_set')
            logger.error(f"Connection details: User={mongo_user}, DB={mongo_db}")
            raise OperationFailure(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while connecting to MongoDB: {str(e)}"
            logger.error(error_msg)
            raise

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

# Create a global instance
db_connection = DatabaseConnection()
