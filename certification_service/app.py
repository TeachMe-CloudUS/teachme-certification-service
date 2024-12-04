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
        # Delete all certificate of one student by student_id
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
