import unittest
from unittest.mock import MagicMock, patch
from certification_service.kafka.producer import send_certification_notification, create_payload
from certification_service.models.student_course_data import Student_Course_Data

class TestKafkaProducer(unittest.TestCase):
    def setUp(self):
        # Create a patch for the producer
        self.producer_patch = patch('certification_service.kafka.producer.producer')
        self.mock_producer = self.producer_patch.start()
        
    def tearDown(self):
        # Stop the patch after each test
        self.producer_patch.stop()

    def test_create_payload_success(self):
        # Test creating a success payload
        payload = create_payload('123', 'course456', True)
        self.assertEqual(payload['status'], 'success')
        self.assertEqual(payload['studentId'], '123')
        self.assertEqual(payload['courseId'], 'course456')

    def test_create_payload_failure(self):
        # Test creating a failure payload
        error_msg = 'Test error'
        payload = create_payload('123', 'course456', False, error_msg)
        self.assertEqual(payload['status'], 'failure')
        self.assertEqual(payload['error'], error_msg)

    def test_send_notification_success(self):
        # Create an instance of Student_Course_Data
        student_course_data = Student_Course_Data(
            student_id='123',
            course_id='course456',
            student_name='John',
            student_surname='Doe',
            student_email='john.doe@example.com'
        )
        # Test sending a success notification
        send_certification_notification(student_course_data, 'blob_url', True)
        
        # Verify producer was called
        self.mock_producer.produce.assert_called_once()
        self.mock_producer.poll.assert_called_once_with(0)

    def test_send_notification_failure(self):
        # Create an instance of Student_Course_Data
        student_course_data = Student_Course_Data(
            student_id='123',
            course_id='course456',
            student_name='John',
            student_surname='Doe',
            student_email='john.doe@example.com'
        )
        # Test sending a failure notification
        send_certification_notification(student_course_data, 'blob_url', False, 'Test error')
        
        # Verify producer was called
        self.mock_producer.produce.assert_called_once()
        self.mock_producer.poll.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
