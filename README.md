
# Certification Service

**Certification Service** is a microservice in the **TeachMe** project, an online learning platform offering video courses. This service is responsible for generating, managing, and validating certificates for students who successfully complete courses. Certificates are digitally signed PDF files stored securely, ensuring authenticity and accessibility.

---

## Features

### Core Capabilities
- **Generate Certificates**: Create signed PDF certificates for students who complete a course.
- **View Certificates**: Retrieve all certificates for a student or a specific course.
- **Delete Certificates**: Remove individual or all certificates for a student.
- **Update Certificates**: Regenerate certificates to reflect updated student information.

### Additional Features
- **Data Validation**: Ensures the integrity of student and course data.
- **Storage Solutions**:
  - MongoDB for metadata storage.
  - Azure Blob Storage for secure and scalable file storage.
- **Event Notifications**:
  - Kafka events notify students when certificates are created.
  - Fully integrated with TeachMe's notification service and frontend.
- **Real-Time Automation**: Automatically generates certificates upon course completion.

---

## Architecture

The service employs a modern microservice architecture designed for scalability and reliability:
- **APIs**: RESTful endpoints for certificate management.
- **Data Storage**:
  - **MongoDB**: Stores student and course metadata along with certificate links.
  - **Azure Blob Storage**: Hosts the actual PDF certificates.
- **Event-Driven Design**: Kafka is used for asynchronous communication and event propagation.
- **Containerization**: Dockerized for consistent deployments across environments.
- **Continuous Integration/Continuous Deployment**: Automated testing and builds with GitHub Actions.

---

## Prerequisites

To run the Certification Service, ensure the following are installed:

- **Development Tools**:
  - Python 3.8+
  - Docker & Docker Compose
- **Services**:
  - MongoDB
  - Azurite (local Azure Blob Storage emulator) or Azure Blob Storage
  - Kafka and Zookeeper

---

## Getting Started

### Clone the Repository
```bash
git clone <repository_url>
cd certification-service
```

### Build and Run with Docker Compose
```bash
docker-compose up --build
```

### Environment Variables
Adapt the docker-compose.yml file with the following variables for your usecase:
```bash
MONGO_DATABASE=certificate_db
MONGO_COLLECTION_NAME=student_certificates
MONGODB_URI_USER=mongodb://user:pass@certification_mongodb:27017/certificate_db?authSource=admin
AZURE_STORAGE_ACCOUNT_NAME=devstoreaccount1
AZURE_STORAGE_ACCOUNT_KEY=your_storage_account_key
BLOB_STORAGE_CONTAINER_NAME=certificates
KAFKA_BOOTSTRAP_SERVER=kafka:9092
```

### Run Tests
```bash
docker-compose run test_runner
```

---

## API Documentation

The Certification Service exposes a set of RESTful APIs for certificate management. 

For detailed API documentation and usage examples, visit the **Swagger UI**:
- Swagger is available at: `http://<host>:<port>/apidocs` (e.g., `http://localhost:8080/apidocs/`).

---

## Technologies Used

- **Storage**: MongoDB, Azure Blob Storage
- **Messaging**: Apache Kafka
- **Testing**: Pytest, Cypress (UI tests)
- **Deployment**: Docker, GitHub Actions

---

## TeachMe Integration

The **Certification Service** is fully integrated into the TeachMe platform:
- Students can view and download their certificates from the TeachMe frontend.
- Course completion events trigger certificate generation via Kafka.
- Notifications are displayed in the TeachMe app when new certificates are available.

---

## License

This project is licensed under the [MIT License](LICENSE).

For questions or further assistance, please contact the TeachMe development team.
