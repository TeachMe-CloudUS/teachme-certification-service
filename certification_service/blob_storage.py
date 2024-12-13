import os
import logging
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class BlobStorageService:
    def __init__(self, connection_string=None, container_name=None):
        """
        Initialize Azure Blob Storage with configuration and operations
        
        :param connection_string: Azure Storage connection string
        :param container_name: Name of the blob container
        """
        try:
            # Configuration
            self.connection_string = connection_string or os.getenv('BLOB_STORAGE_CONNECTION_STRING')
            logger.info(f"Using connection string: {self.connection_string}")
            
            self.container_name = container_name or os.getenv('BLOB_STORAGE_CONTAINER_NAME')
            logger.info(f"Using container name: {self.container_name}")
            
            # Validate configuration
            if not self.connection_string:
                raise ValueError("Azure Blob Storage connection string is required")
            
            logger.info("Creating Azure Blob Storage client...")
            # Create blob service client
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            
            logger.info("Creating Azure Blob Storage container...")
            # Create container if it doesn't exist
            self._create_container_if_not_exists()
            
            logger.info("Getting Azure Blob Storage container client...")
            # Get container client
            self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage: {e}")
            # Optionally, you can choose to re-raise the exception or handle it differently
            raise

    def _create_container_if_not_exists(self):
        """Create the blob container if it does not exist"""
        try:
            self.blob_service_client.create_container(
                name=self.container_name, 
                public_access='blob'
            )
            logger.info(f"Container '{self.container_name}' created successfully")
        except ResourceExistsError:
            logger.info(f"Container '{self.container_name}' already exists")
        except Exception as e:
            logger.error(f"Error creating container: {e}")
            raise

    def list_blobs(self):
        """List all blobs in the container"""
        try:
            blobs = [blob.name for blob in self.container_client.list_blobs()]
            logger.info(f"Listed {len(blobs)} blobs in container")
            return blobs
        except Exception as e:
            logger.error(f"Error listing blobs: {e}")
            raise

    def upload_file_from_stream(self, file_stream, blob_name):
        """Upload a file-like object directly to Azure Blob Storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            file_stream.seek(0)
            blob_client.upload_blob(file_stream, overwrite=True)
            logger.info(f"File uploaded successfully to {blob_name}")
            return blob_client.url
        except Exception as e:
            logger.error(f"Error uploading file stream to {blob_name}: {e}")
            raise

    def download_file(self, blob_name, download_path):
        """Download a file from Azure Blob Storage"""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            with open(download_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            logger.info(f"File {blob_name} downloaded successfully to {download_path}")
        except Exception as e:
            logger.error(f"Error downloading blob {blob_name}: {e}")
            raise

# Create a global instance for easy import
blob_storage_service = BlobStorageService()