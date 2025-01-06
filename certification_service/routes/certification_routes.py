# routes/certification_routes.py
from flask import Blueprint, jsonify, request
from certification_service.course_cert_utils import (certify_student, get_all_certs, get_cert, delete_all_certs)
from certification_service.models.student_course_data import Student_Course_Data
from certification_service.database import db_connection
from flasgger import swag_from

certification_bp = Blueprint('certification', __name__)

@certification_bp.route('/api/v1/certify', methods=['POST'])
@swag_from('swagger_docs/certify_student.yml')
def route_certify():
    """Certify a student by generating a PDF certificate."""
    # Assuming the request body contains the necessary data
    data = request.get_json()
    try:
        student_course_data = Student_Course_Data(
        student_id=data.get('student_id'),
        student_userId=data.get('student_userId'),
        student_name=data.get('student_name'),
        student_surname=data.get('student_surname'),
        student_email=data.get('student_email'),
        course_id=data.get('course_id'),
        course_name=data.get('course_name'),
        course_description=data.get('course_description'),
        course_duration=data.get('course_duration'),
        course_level=data.get('course_level'),
        completionDate=data.get('completionDate'))
        
        success = certify_student(student_course_data)
        if not success:
            return jsonify({
                "Error": "Certification failed",
                "Reason": "Certificate already exists"
            }), 409
        return jsonify({"success": success}), 201
        
    except ValueError as e:
        return jsonify({
            "Error": f"Certification failed: {str(e)}"
        }), 400

@certification_bp.route('/api/v1/certificates/<string:student_id>', methods=['GET'])
@swag_from('swagger_docs/get_all_student_certificates.yml')
def route_get_all_certificates(student_id):
    """Get all certificates for a student."""
    certificates = get_all_certs(student_id)
    if not certificates:
        return jsonify({"message": "No certificates found for this student."}), 404
    return jsonify(certificates), 200

@certification_bp.route('/api/v1/certificates/<string:student_id>/<string:course_id>', methods=['GET'])
@swag_from('swagger_docs/get_course_certificate.yml')
def route_get_course_certificate(student_id, course_id):
    """Get certificate for a specific course and student."""
    certificate = get_cert(student_id, course_id)
    if not certificate:
        return jsonify({"error": "Certificate not found"}), 404

    return jsonify(certificate), 200

@certification_bp.route('/api/v1/certificates/<string:student_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_all_student_certificates.yml')
def route_delete_all_student_certificates(student_id):
    """Delete all certificates for a student."""
    try:
        deleted_cert_count = delete_all_certs(student_id)

        if deleted_cert_count == 0:
            return jsonify({"message": f"No certificates found for student ID {student_id}."}), 404

        return jsonify({"message": f"Deleted {deleted_cert_count} certificate(s) for student ID {student_id}."}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete certificates for student ID {student_id}: {str(e)}"}), 500


@certification_bp.route('/api/v1/certificates/<string:student_id>/<string:course_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_course_certificate.yml')
def route_delete_course_certificate(student_id, course_id):
    """Delete a specific certificate for a student."""
    try:
        deleted, message = delete_certificate(student_id, course_id)
        if deleted:
            return jsonify({"message": message}), 200
        return jsonify({"message": message}), 400

    except Exception as e:
        return jsonify({"error": f"Failed to delete certificate for student ID {student_id} "
                                  f"and course ID {course_id}: {str(e)}"}), 500
        
        
        
@certification_bp.route('/api/v1/certificates/<string:student_id>/<string:course_id>', methods=['PUT'])
@swag_from('swagger_docs/update_course_certificate.yml')
def route_update_course_certificate(student_id, course_id):
    """Update a certificate by deleting the old one and setting a new student name."""
    data = request.get_json()

    try:
        # Check if the certificate exists
        existing_cert = get_cert(student_id, course_id)
        if not existing_cert:
            return jsonify({"error": "Certificate not found"}), 404

        # Delete the existing certificate
        delete_success = delete_certificate(student_id, course_id)
        if not delete_success:
            return jsonify({"error": "Failed to delete the existing certificate"}), 500

        # Get the new student name from the request data
        new_student_name = data.get('new_student_name')
        if not new_student_name:
            return jsonify({"error": "New student name is required"}), 400

        # Create a new certificate with the new student name
        new_cert = Student_Course_Data(
            student_id=student_id,
            student_userId=existing_cert.student_userId,
            student_name=new_student_name,
            student_surname=existing_cert.student_surname,
            student_email=existing_cert.student_email,
            course_id=course_id,
            course_name=existing_cert.course_name,
            course_description=existing_cert.course_description,
            course_duration=existing_cert.course_duration,
            course_level=existing_cert.course_level,
            completionDate=existing_cert.completionDate
        )

        # Certify the student with the new name
        certify_success = certify_student(new_cert)
        if not certify_success:
            return jsonify({"error": "Failed to certify the student with the new name"}), 500

        return jsonify({"message": "Certificate updated with new student name successfully"}), 200

    except ValueError as e:
        return jsonify({"error": f"Operation failed: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred while updating the certificate: {str(e)}"}), 500

 