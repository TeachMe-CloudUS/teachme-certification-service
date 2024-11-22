# Student Certification Microservices

## Overview
This project implements a microservices architecture for student certification using Python.

## Services
1. Student Information Service: Manages student data
2. PDF Certification Service: Generates student certificates
3. Event Notification Service: Handles event streaming

## Setup
1. Create a virtual environment
```bash
python3 -m venv venv
```

2. Activate the virtual environment
```bash
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run Services
- Student Info Service: `python student_service/app.py`
- PDF Certification Service: `python certification_service/app.py`
- Event Service: `python event_service/app.py`

5. Run the certification service
```bash
python certification_service/app.py
```

6. Test the certification endpoint
```bash
curl -X POST http://127.0.0.1:5002/certify/1
```

## Certificates Storage
Certificates are stored in the `certificates` directory within the project.

## Testing
Run tests with: `pytest`
