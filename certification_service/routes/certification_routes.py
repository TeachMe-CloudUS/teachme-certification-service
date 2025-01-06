# routes/certification_routes.py
from flask import Blueprint, jsonify, request
from certification_service.course_cert_utils import (certify_student, get_all_certs, get_cert, delete_all_certs)
from certification_service.models.student_course_data import Student_Course_Data

certification_bp = Blueprint('certification', __name__)

@certification_bp.route('/api/v1/certify/<int:student_id>/<int:course_id>', methods=['POST'])
def route_certify_student(student_id, course_id):
    """Certify a student by generating a PDF certificate."""
    student_course_data = Student_Course_Data(
        student_id=str(student_id),
        course_id=str(course_id),
    )
    success = certify_student(student_course_data)
    return jsonify({"success": success}), 201 if success else 400

@certification_bp.route('/api/v1/certify', methods=['POST'])
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

@certification_bp.route('/api/v1/certificates/<int:student_id>', methods=['GET'])
def route_get_all_certificates(student_id):
    """Get all certificates for a student."""
    certificates = get_all_certs(student_id)
    return jsonify(certificates), 200

@certification_bp.route('/api/v1/certificates/<int:student_id>/<int:course_id>', methods=['GET'])
def route_get_course_certificate(student_id, course_id):
    """Get certificate for a specific course and student."""
    certificate = get_cert(student_id, course_id)
    if certificate:
        return jsonify(certificate), 200 
    return jsonify({"error": "Certificate not found"}), 404

@certification_bp.route('/api/v1/certificates/<int:student_id>', methods=['DELETE'])
def route_delete_student_certificates(student_id):
    """Delete all certificates for a student."""
    try:
        deleted_cert_count = delete_all_certs(student_id)
        return jsonify({"message": f"Deleted {deleted_cert_count} certificate(s) for"
                        f"student ID {student_id}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete certificates for"
                        f"student ID {student_id}: {str(e)}"}), 500

@certification_bp.route('/api/v1/certificates/<int:student_id>/<int:course_id>', methods=['DELETE'])
def route_delete_certificate(student_id, course_id):
    """Delete a specific certificate for a student."""
    try:
        deleted, message = delete_certificate(student_id, course_id)
        if deleted:
            return jsonify({"message": message}), 200
        return jsonify({"message": message}), 400 
    except Exception as e:
        return jsonify({"error": f"Failed to delete certificate for student ID {student_id}"
                        f"and course ID {course_id}: {str(e)}"}), 500