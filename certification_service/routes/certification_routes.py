# routes/certification_routes.py
from flask import Blueprint, jsonify
from certification_service.course_cert_utils import (certify_student, get_all_certs, get_cert, delete_all_certs)

certification_bp = Blueprint('certification', __name__)

@certification_bp.route('/certify/<int:student_id>/<int:course_id>', methods=['POST'])
def route_certify_student(student_id, course_id):
    """Certify a student by generating a PDF certificate."""
    success = certify_student(student_id, course_id)
    return jsonify({"success": success}), 200 if success else 400

@certification_bp.route('/certify', methods=['POST'])
def route_certify():
    """Certify a student by generating a PDF certificate."""
    success = certify_student(None, None)
    if not success:
        return jsonify({
            "Error": "Certification failed, possible reasons: "
            "Certificate already exists or missing or invalid student/course data"
        }), 500
    return jsonify({"success": success}), 200

@certification_bp.route('/certificates/<int:student_id>', methods=['GET'])
def route_get_all_certificates(student_id):
    """Get all certificates for a student."""
    certificates = get_all_certs(student_id)
    return jsonify(certificates), 200

@certification_bp.route('/certificates/<int:student_id>/<int:course_id>', methods=['GET'])
def route_get_course_certificate(student_id, course_id):
    """Get certificate for a specific course and student."""
    certificate = get_cert(student_id, course_id)
    return jsonify(certificate), 200

@certification_bp.route('/certificates/<int:student_id>', methods=['DELETE'])
def route_delete_student_certificates(student_id):
    """Delete all certificates for a student."""
    try:
        deleted_cert_count = delete_all_certs(student_id)
        return jsonify({"message": f"Deleted {deleted_cert_count} certificate(s) for student ID {student_id}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete certificates for student ID {student_id}: {str(e)}"}), 500


####################################################################
#########################Lydia######################################
####################################################################
# # Route to certify a student
# @app.route('/certify/<int:student_id>/<int:course_id>', methods=['POST'])
# def certify_student(student_id,course_id):
#     """Certify a student by generating a PDF certificate."""
#     try:
#         # Get mock student data
#         student_data = get_mock_student_data(student_id)
        
#         # Generate Certificate
#         certificate_path = generate_certificate(student_data,course_id)
        
#         # Store certificate in database
#         certificate_data = {
#             'student_id': student_id,
#             'name': student_data['name'],
#             'certificate_path': certificate_path,
#             'course': student_data['course'],
#             'created_at': datetime.now(),
#             'status': 'COMPLETED'
#         }
        
#         try:
#             stored_cert = db_connection.store_certificate(certificate_data)
#             logger.info("Certificate stored in database successfully")
#         except Exception as e:
#             logger.error(f"Failed to store certificate in database: {str(e)}")
#             # Continue even if database storage fails
#             stored_cert = None

#         # Only produce the "certificate generated" event if certificate creation and storage are successful
#         if stored_cert:
#             #topic_name = create_topic_name('certification_service', 'certificate', 'generated', 'v1')
#             #producer = kafka_producer_config()  
#             #event = KafkaEvent(service='certification_service', entity='certificate', action='generated', version='v1')
#             #produce_event(producer, topic_name, key=str(student_id), event=event)
#             logger.info(f"Event sent to Kafka: {event.to_json()}")
        
#         return jsonify({
#             'message': 'Certificate generated successfully',
#             'certificate_path': certificate_path,
#             'stored_in_db': stored_cert is not None
#         }), 200
    
        
#     # Log the event
#         logger.info("Certificate generated successfully: %s", json.dumps({
#             'student_id': student_id,
#             'certificate_path': certificate_path
#         }))
        
#         return jsonify({
#             'message': 'Certificate generated successfully',
#             'certificate_path': certificate_path,
#             'stored_in_db': stored_cert is not None
#         }), 200
    
#     except Exception as e:
#         error_msg = str(e)
#         logger.error(f"Failed to generate certificate: {error_msg}")
#         return jsonify({'error': error_msg}), 500
    
# def update_certificates_for_student(student_id, user_id, phone_number, plan):
#     """
#     Update certificates for a student by:
#     1. Deleting old certificates.
#     2. Creating new certificates with updated data.
#     """
#     try:
#         # Step 1: Delete old certificates (you would need a method to delete from DB or File System)
#         print(f"Deleting old certificates for student {student_id}...")
#         # Example function to delete certificates (implement based on your storage method)
#         # delete_certificates(student_id)

#         # Step 2: Generate a new certificate
#         print(f"Creating new certificate for student {student_id} with updated data...")
        
#         # Get mock student data (this would be fetched from the actual database or API)
#         student_data = get_mock_student_data(student_id)  # Replace this with your actual student data retrieval method
        
#         # Generate the new certificate (this would call a function like `generate_certificate` for PDF creation)
#         course_id = "updated_course"  # Example, you may retrieve the course ID from the updated event
#         certificate_path = generate_certificate(student_data, course_id)

#         # Prepare certificate data to be stored
#         certificate_data = {
#             'student_id': student_id,
#             'name': student_data['name'],
#             'certificate_path': certificate_path,
#             'course': student_data['course'],
#             'created_at': datetime.now(),
#             'status': 'COMPLETED'
#         }

#         # Step 3: Store the new certificate in the database
#         try:
#             stored_cert = db_connection.store_certificate(certificate_data)
#             print("Certificate stored in database successfully")
#         except Exception as e:
#             print(f"Failed to store certificate in database: {str(e)}")
#             stored_cert = None

       
#         # Only produce the "certificate updated" event if certificate creation and storage are successful
#         if stored_cert:
#             #topic_certificate_updated = create_topic_name('certification_service', 'certificate', 'updated', 'v2')
#             #producer = kafka_producer_config() 
#             event = KafkaEvent(service='certification_service', entity='certificate', action='updated', version='v2')
#             #produce_event(producer, topic_certificate_updated, key=str(student_id), event=event)
#             logger.info(f"Event sent to Kafka: {event.to_json()}")

#         # Return success response
#         return jsonify({
#             'message': 'Certificate updated successfully',
#             'certificate_path': certificate_path,
#             'stored_in_db': stored_cert is not None
#         }), 200

#         # Log the event
#         print(f"Certificate generated successfully for student {student_id}: {certificate_path}")
        
#         # Return success response
#         return jsonify({
#             'message': 'Certificate generated successfully',
#             'certificate_path': certificate_path,
#             'stored_in_db': stored_cert is not None
#         }), 200

#     except Exception as e:
#         error_msg = str(e)
#         print(f"Failed to update certificates for student {student_id}: {error_msg}")
#         return jsonify({'error': error_msg}), 500


# # Get all certificates of one student by student_id
# @app.route('//certificates/<student_id>', methods=['GET'])
# def get_all_coures_certificates(student_id):
#     """---Get all certificates of one student by student_id---"""
#     try:  
#         # Get all certificates of one student by student_id
#         # Prüfen, ob es den Studenten gibt 
        
#         #all_student_certificates = db_connection.get_certificates_by_student_id(student_id)
#         all_student_certificates = "Expert in Coding without Highling"
#         if not all_student_certificates:
#             return jsonify({"message": "No certificates found for this student"}), 404

#         return jsonify(all_student_certificates), 200
    
#     except Exception as e:
#         app.logger.error(f"Error retrieving certificates for student_id {student_id}: {str(e)}")
#         return jsonify({"error": "Failed to retrieve certificates"}), 500
    
# # Get the certificate of one course absolved by one student by student_id and course_id
# @app.route('/certificates/<int:student_id>/course/<int:course_id>', methods=['GET'])   
# def get_one_course_certificate(student_id, course_id):
#     """---Get the certificate of one course absolved by one student by student_id and course_id---"""
#     try:
#         # Get the certificate of one course absolved by one student by student_id and course_id
#         #course_certificate = db_connection.get_certificate_by_student_id_and_course_id(student_id, course_id)
#         course_certificate = "Expert in Coding without Highling"
#         if not course_certificate:
#             return jsonify({"message": "No certificate found for student ID {student_id} in course ID {course_id}"}), 404

#         return jsonify(course_certificate), 200
#     except Exception as e:
#         app.logger.error(f"Error retrieving certificate for student_id {student_id} and course_id {course_id}: {str(e)}")
#         return jsonify({"error": "Failed to retrieve certificate"}), 500

# # Delete all certificate of one student by student_id
# @app.route('/certificates/<int:student_id>', methods=['DELETE'])
# def delete_all_student_certificates(student_id):
#     """---Delete all certificate of one student by student_id---"""
#     try:
#         #deleted_certificates = db_connection.delete_certificates_by_student_id(student_id)
#         #deleted_count = len(deleted_certificates)
#         deleted_certificates="adas"
#         deleted_count = 69
#         if not deleted_certificates:
#             return jsonify({"message": "No certificates found for this student"}), 404

#         return jsonify({"message": f"Deleted {deleted_count} certificate(s) for student ID {student_id}"}), 200
#     except Exception as e:
#         app.logger.error(f"Error deleting certificates for student_id {student_id}: {str(e)}")
#         return jsonify({"error": "Failed to delete certificates"}), 500
    

