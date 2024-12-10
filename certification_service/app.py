# app.py
"""
This module provides a certification service using Flask.
"""
import os
import subprocess
import io
import json
from datetime import datetime
from flask import Flask, jsonify
from dotenv import load_dotenv
from database import db_connection, get_mock_student_data
from health import HealthCheck
from course_cert_generator import generate_certificate
from cert_management import ensure_certificate_and_key_exist
from logger import logger
from kafka_main import produce_certificate_generated_event, kafka_producer_config, produce_event
from kafka_utils import create_topic_name, KafkaProducer, KafkaEvent
from config import CERTIFICATES_DIR

# Load environment variables from .env file 
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize database connection
try:
    db_connection.init_mongodb()
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

# Initialize health checker
health_checker = HealthCheck(
    service_name='certification-service',
    dependencies={
        'database': db_connection,
        'certificates_dir': CERTIFICATES_DIR
    }
)

# Call the function to ensure the certificate, key, and PFX file exist
ensure_certificate_and_key_exist()

# Route to certify a student
@app.route('/certify/<int:student_id>/<int:course_id>', methods=['POST'])
def certify_student(student_id,course_id):
    """Certify a student by generating a PDF certificate."""
    try:
        # Get mock student data
        student_data = get_mock_student_data(student_id)
        
        # Generate Certificate
        certificate_path = generate_certificate(student_data,course_id)
        
        # Store certificate in database
        certificate_data = {
            'student_id': student_id,
            'name': student_data['name'],
            'certificate_path': certificate_path,
            'course': student_data['course'],
            'created_at': datetime.now(),
            'status': 'COMPLETED'
        }
        
        try:
            stored_cert = db_connection.store_certificate(certificate_data)
            logger.info("Certificate stored in database successfully")
        except Exception as e:
            logger.error(f"Failed to store certificate in database: {str(e)}")
            # Continue even if database storage fails
            stored_cert = None

        # Only produce the "certificate generated" event if certificate creation and storage are successful
        if stored_cert:
            topic_name = create_topic_name('certification_service', 'certificate', 'generated', 'v1')
            producer = kafka_producer_config()  
            event = KafkaEvent(service='certification_service', entity='certificate', action='generated', version='v1')
            produce_event(producer, topic_name, key=str(student_id), event=event)
            logger.info(f"Event sent to Kafka: {event.to_json()}")
        
        return jsonify({
            'message': 'Certificate generated successfully',
            'certificate_path': certificate_path,
            'stored_in_db': stored_cert is not None
        }), 200
    
        
    # Log the event
        logger.info("Certificate generated successfully: %s", json.dumps({
            'student_id': student_id,
            'certificate_path': certificate_path
        }))
        
        return jsonify({
            'message': 'Certificate generated successfully',
            'certificate_path': certificate_path,
            'stored_in_db': stored_cert is not None
        }), 200
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to generate certificate: {error_msg}")
        return jsonify({'error': error_msg}), 500
    
def update_certificates_for_student(student_id, user_id, phone_number, plan):
    """
    Update certificates for a student by:
    1. Deleting old certificates.
    2. Creating new certificates with updated data.
    """
    try:
        # Step 1: Delete old certificates (you would need a method to delete from DB or File System)
        print(f"Deleting old certificates for student {student_id}...")
        # Example function to delete certificates (implement based on your storage method)
        # delete_certificates(student_id)

        # Step 2: Generate a new certificate
        print(f"Creating new certificate for student {student_id} with updated data...")
        
        # Get mock student data (this would be fetched from the actual database or API)
        student_data = get_mock_student_data(student_id)  # Replace this with your actual student data retrieval method
        
        # Generate the new certificate (this would call a function like `generate_certificate` for PDF creation)
        course_id = "updated_course"  # Example, you may retrieve the course ID from the updated event
        certificate_path = generate_certificate(student_data, course_id)

        # Prepare certificate data to be stored
        certificate_data = {
            'student_id': student_id,
            'name': student_data['name'],
            'certificate_path': certificate_path,
            'course': student_data['course'],
            'created_at': datetime.now(),
            'status': 'COMPLETED'
        }

        # Step 3: Store the new certificate in the database
        try:
            stored_cert = db_connection.store_certificate(certificate_data)
            print("Certificate stored in database successfully")
        except Exception as e:
            print(f"Failed to store certificate in database: {str(e)}")
            stored_cert = None

       
        # Only produce the "certificate updated" event if certificate creation and storage are successful
        if stored_cert:
            topic_certificate_updated = create_topic_name('certification_service', 'certificate', 'updated', 'v2')
            producer = kafka_producer_config() 
            event = KafkaEvent(service='certification_service', entity='certificate', action='updated', version='v2')
            produce_event(producer, topic_certificate_updated, key=str(student_id), event=event)
            logger.info(f"Event sent to Kafka: {event.to_json()}")

        # Return success response
        return jsonify({
            'message': 'Certificate updated successfully',
            'certificate_path': certificate_path,
            'stored_in_db': stored_cert is not None
        }), 200

        # Log the event
        print(f"Certificate generated successfully for student {student_id}: {certificate_path}")
        
        # Return success response
        return jsonify({
            'message': 'Certificate generated successfully',
            'certificate_path': certificate_path,
            'stored_in_db': stored_cert is not None
        }), 200

    except Exception as e:
        error_msg = str(e)
        print(f"Failed to update certificates for student {student_id}: {error_msg}")
        return jsonify({'error': error_msg}), 500


# Get all certificates of one student by student_id
@app.route('//certificates/<student_id>', methods=['GET'])
def get_all_coures_certificates(student_id):
    """---Get all certificates of one student by student_id---"""
    try:  
        # Get all certificates of one student by student_id
        # Prüfen, ob es den Studenten gibt 
        
        all_student_certificates = db_connection.get_certificates_by_student_id(student_id)

        if not all_student_certificates:
            return jsonify({"message": "No certificates found for this student"}), 404

        return jsonify(all_student_certificates), 200
    
    except Exception as e:
        app.logger.error(f"Error retrieving certificates for student_id {student_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve certificates"}), 500
    
# Get the certificate of one course absolved by one student by student_id and course_id
@app.route('/certificates/<int:student_id>/course/<int:course_id>', methods=['GET'])   
def get_one_course_certificate(student_id, course_id):
    """---Get the certificate of one course absolved by one student by student_id and course_id---"""
    try:
        # Get the certificate of one course absolved by one student by student_id and course_id
        course_certificate = db_connection.get_certificate_by_student_id_and_course_id(student_id, course_id)

        if not course_certificate:
            return jsonify({"message": "No certificate found for student ID {student_id} in course ID {course_id}"}), 404

        return jsonify(course_certificate), 200
    except Exception as e:
        app.logger.error(f"Error retrieving certificate for student_id {student_id} and course_id {course_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve certificate"}), 500

# Delete all certificate of one student by student_id
@app.route('/certificates/<int:student_id>', methods=['DELETE'])
def delete_all_student_certificates(student_id):
    """---Delete all certificate of one student by student_id---"""
    try:
        deleted_certificates = db_connection.delete_certificates_by_student_id(student_id)
        deleted_count = len(deleted_certificates)

        if not deleted_certificates:
            return jsonify({"message": "No certificates found for this student"}), 404

        return jsonify({"message": f"Deleted {deleted_count} certificate(s) for student ID {student_id}"}), 200
    except Exception as e:
        app.logger.error(f"Error deleting certificates for student_id {student_id}: {str(e)}")
        return jsonify({"error": "Failed to delete certificates"}), 500
    
# Health check endpoint to verify service and dependency health
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint that verifies service and dependency health."""
    return jsonify(*health_checker.get_health_status())

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
