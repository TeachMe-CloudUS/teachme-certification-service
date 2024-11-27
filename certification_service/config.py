import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Certificate Configuration
CERTIFICATES_DIR = os.getenv('CERTIFICATES_DIR')
PFX_PASSPHRASE = os.getenv('PFX_PASSPHRASE')

# Course Certificate Configuration
QR_CODE_URL = os.getenv('QR_CODE_URL')
SIGNATURE_FIELD_NAME = os.getenv('SIGNATURE_FIELD_NAME')
SIGNATURE_BOX = tuple(map(float, os.getenv('SIGNATURE_BOX').split(',')))

# MongoDB Configuration
MONGODB_URI_ADMIN = os.getenv('MONGODB_URI_ADMIN')
MONGODB_URI_USER = os.getenv('MONGODB_URI_USER')