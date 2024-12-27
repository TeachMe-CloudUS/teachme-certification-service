import unittest
from unittest.mock import MagicMock, patch
from certification_service.kafka.producer import send_certification_notification, create_payload

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
        # Test sending a success notification
        send_certification_notification('123', 'course456', True)
        
        # Verify producer was called
        self.mock_producer.produce.assert_called_once()
        self.mock_producer.poll.assert_called_once_with(0)

    def test_send_notification_failure(self):
        # Test sending a failure notification
        send_certification_notification('123', 'course456', False, 'Test error')
        
        # Verify producer was called
        self.mock_producer.produce.assert_called_once()
        self.mock_producer.poll.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
