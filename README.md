# Student Certification Microservice

## Overview
This microservice is part of the TeachMe platform, responsible for generating and managing student certificates. It provides a RESTful API for certificate generation and verification.

## Features
- PDF Certificate Generation
- QR Code Integration
- Digital Signatures
- MongoDB Storage for Certificate Records

## Prerequisites
- Docker and Docker Compose
- Python 3.8 or higher (for local development)
- MongoDB

## Configuration
1. Create a `.env` file in the root directory with the following variables:
```env
# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=rootpassword123
MONGO_USERNAME=certification_service
MONGO_PASSWORD=userpassword123
MONGO_DATABASE=certificate_db
MONGO_PORT=27017
MONGO_HOST=mongodb

# Certificate Configuration
PFX_PASSPHRASE=mysecurepassphrase
SIGNATURE_FIELD_NAME=Signature1
SIGNATURE_BOX=150,30,450,90
QR_CODE_URL=your-verification-url
```

## Setup and Running

### Using Docker (Recommended)
1. Build and start the services:
```bash
docker-compose up --build
```

2. To run in detached mode:
```bash
docker-compose up -d
```

### Local Development
1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # Unix/macOS
.\venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the service:
```bash
python -m flask run
```

## Monitoring and Logs

### View Container Logs
1. Real-time logs (follow mode):
```bash
docker logs -f certification_service
```

2. View last N lines:
```bash
docker logs --tail 100 certification_service
```

3. View logs since specific time:
```bash
docker logs --since 1h certification_service
```

4. Using Docker Compose:
```bash
docker-compose logs -f certification_service
```

## API Endpoints

### Generate Certificate
```bash
POST /certify/{user_id}
```

### Verify Certificate
```bash
GET /verify/{certificate_id}
```

## Testing
Run the test suite:
```bash
pytest
```

## Certificates Storage
Generated certificates are stored in the `certificates` directory and their metadata in MongoDB.

## Troubleshooting
1. If MongoDB connection fails:
   - Check if MongoDB container is running: `docker ps`
   - Verify environment variables in `.env`
   - Check MongoDB logs: `docker logs certification_mongodb`

2. If certificate generation fails:
   - Ensure the certificates directory exists and is writable
   - Verify PFX file configuration
   - Check application logs for detailed error messages
