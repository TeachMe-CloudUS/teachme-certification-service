from confluent_kafka import Producer
import json
from certification_service.logger import logger

# Kafka Producer Configuration
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',  # Ensure all replicas confirm the message
    'retries': 5     # Retry sending messages up to 5 times
})

def delivery_report(err, msg):
    """
    Callback function triggered after each message is produced.

    Args:
        err (KafkaError): The error occurred during delivery, or None if delivery succeeded.
        msg (Message): The produced message.
    """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def create_payload(student_id, course_id, success, error_message=None):
    """
    Creates the payload for the Kafka message.

    Args:
        student_id (str): The ID of the student.
        course_id (str): The ID of the course.
        success (bool): True if the certification was successful, False otherwise.
        error_message (str, optional): The error message if certification failed.

    Returns:
        dict: The message payload.
    """
    if success:
        return {
            "studentId": student_id,
            "courseId": course_id,
            "status": "success",
            "message": f"Student with ID {student_id} for Course {course_id} was successfully certified."
        }
    return {
        "studentId": student_id,
        "courseId": course_id,
        "status": "failure",
        "error": error_message,
        "message": f"Certification failed for student with ID {student_id} and course {course_id}."
    }

def send_certification_notification(student_id, course_id, success, error_message=None):
    """
    Sends a Kafka message indicating whether a student's certification was successful or failed.

    Args:
        student_id (str): The ID of the student.
        course_id (str): The ID of the course.
        success (bool): True if the certification was successful, False if it failed.
        error_message (str, optional): The error message if the certification failed.
    """
    if not student_id or not course_id:
        logger.error("Invalid student_id or course_id provided.")
        return

    certification_topic = 'certification-status'  # The Kafka topic for certification status updates
    payload = create_payload(student_id, course_id, success, error_message)

    try:
        # Send the payload to the specified topic, with delivery_report as the callback
        producer.produce(
            certification_topic,
            json.dumps(payload).encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)  # Non-blocking call to handle delivery reports
        logger.info(f'Message sent to {certification_topic}: {payload}')
    except Exception as e:
        logger.error(f'Failed to send message for student {student_id}: {e} and course {course_id}')

def close_producer():
    """
    Ensures all pending messages are delivered before shutting down the producer.
    """
    try:
        producer.flush()  # Wait for any outstanding messages to be sent
        logger.info("Kafka producer flushed and closed.")
    except Exception as e:
        logger.error(f"Error while closing producer: {e}")
