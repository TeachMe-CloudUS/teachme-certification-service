import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Certificate Configuration
CERTIFICATES_DIR = os.getenv('CERTIFICATES_DIR')
PFX_PASSPHRASE = os.getenv('PFX_PASSPHRASE')

# Course Certificate Configuration
QR_CODE_URL = os.getenv('QR_CODE_URL')
SIGNATURE_FIELD_NAME = os.getenv('SIGNATURE_FIELD_NAME')
SIGNATURE_BOX = tuple(map(float, os.getenv('SIGNATURE_BOX', '50,50,200,200').split(',')))

# MongoDB Configuration
MONGODB_URI_ADMIN = os.getenv('MONGODB_URI_ADMIN')
MONGODB_URI_USER = os.getenv('MONGODB_URI_USER')

def validate_environment_variables():
    """Validate that all required environment variables are set."""
    # List of required environment variables
    required_vars = [
        # # Azure Blob Storage Configuration
        # 'AZURE_STORAGE_CONNECTION_STRING',
        # 'AZURE_STORAGE_CONTAINER_NAME',
        
        # Certificate Generation Configuration
        'QR_CODE_URL',
        'SIGNATURE_FIELD_NAME',
        'SIGNATURE_BOX',
        
        # MongoDB Configuration
        'MONGODB_URI_ADMIN',
        'MONGODB_URI_USER',
        
        'CERTIFICATES_DIR',
        'PFX_PASSPHRASE'
    ]
    
    # Check for missing variables
    missing_vars = [var for var in required_vars if os.getenv(var) is None]
    
    # Raise an error if any variables are missing
    if missing_vars:
        error_message = (
            "The following required environment variables are missing:\n" +
            "\n".join(f"- {var}" for var in missing_vars)
        )
        logger.error(error_message)
        raise EnvironmentError(error_message)
    
    logger.info("All required environment variables are present.")

# Validate environment variables when the config module is imported
validate_environment_variables()