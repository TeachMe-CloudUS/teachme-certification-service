# routes/certification_routes.py
from flask import Blueprint, jsonify
from certification_service.course_cert_utils import (certify_student, get_all_certs, get_cert, delete_all_certs)

certification_bp = Blueprint('certification', __name__)

@certification_bp.route('/api/v1/certify/<int:student_id>/<int:course_id>', methods=['POST'])
def route_certify_student(student_id, course_id):
    """Certify a student by generating a PDF certificate."""
    success = certify_student(student_id, course_id)
    return jsonify({"success": success}), 200 if success else 400

@certification_bp.route('/api/v1/certify', methods=['POST'])
def route_certify():
    """Certify a student by generating a PDF certificate."""
    success = certify_student(None, None)
    if not success:
        return jsonify({
            "Error": "Certification failed, possible reasons: "
            "Certificate already exists or missing or invalid student/course data"
        }), 500
    return jsonify({"success": success}), 200

@certification_bp.route('/api/v1/certificates/<int:student_id>', methods=['GET'])
def route_get_all_certificates(student_id):
    """Get all certificates for a student."""
    certificates = get_all_certs(student_id)
    return jsonify(certificates), 200

@certification_bp.route('/api/v1/certificates/<int:student_id>/<int:course_id>', methods=['GET'])
def route_get_course_certificate(student_id, course_id):
    """Get certificate for a specific course and student."""
    certificate = get_cert(student_id, course_id)
    return jsonify(certificate), 200

@certification_bp.route('/api/v1/certificates/<int:student_id>', methods=['DELETE'])
def route_delete_student_certificates(student_id):
    """Delete all certificates for a student."""
    try:
        deleted_cert_count = delete_all_certs(student_id)
        return jsonify({"message": f"Deleted {deleted_cert_count} certificate(s) for student ID {student_id}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete certificates for student ID {student_id}: {str(e)}"}), 500

