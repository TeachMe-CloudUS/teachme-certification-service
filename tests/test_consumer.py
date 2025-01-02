import unittest
from unittest.mock import MagicMock, patch
from confluent_kafka import KafkaError, Message
from certification_service.kafka.consumer import consume_course_completed_events, create_consumer

class TestKafkaConsumer(unittest.TestCase):
    def setUp(self):
        # Create a mock consumer
        self.mock_consumer = MagicMock()
        
    def test_consumer_empty_message(self):
        # Test handling of empty messages
        self.mock_consumer.poll.return_value = None
        
        # Call consumer with a short timeout and few retries
        consume_course_completed_events(self.mock_consumer, 'test-topic', timeout=0.1, max_empty_polls=1)
        
        # Verify consumer was subscribed and polled
        self.mock_consumer.subscribe.assert_called_once_with(['test-topic'])
        self.mock_consumer.poll.assert_called()

    def test_consumer_valid_message(self):
        # Create a mock message
        mock_msg = MagicMock(spec=Message)
        mock_msg.error.return_value = None
        mock_msg.value.return_value = b'{"studentId": "123", "userId": "789", "courseId": "456"}'
        
        # Set up consumer to return one valid message then None
        self.mock_consumer.poll.side_effect = [mock_msg, None]
        
        # Call consumer
        consume_course_completed_events(self.mock_consumer, 'test-topic', timeout=0.1, max_empty_polls=1)
        
        # Verify consumer processed the message
        self.mock_consumer.subscribe.assert_called_once_with(['test-topic'])
        self.assertEqual(self.mock_consumer.poll.call_count, 2)

    def test_consumer_invalid_message(self):
        # Create a mock message with invalid data
        mock_msg = MagicMock(spec=Message)
        mock_msg.error.return_value = None
        mock_msg.value.return_value = b'{"studentId": 123, "userId": "789", "courseId": 456}'  # Invalid: studentId and courseId should be strings
        
        # Set up consumer to return one invalid message then None
        self.mock_consumer.poll.side_effect = [mock_msg, None]
        
        # Call consumer
        consume_course_completed_events(self.mock_consumer, 'test-topic', timeout=0.1, max_empty_polls=1)
        
        # Verify consumer processed the message
        self.mock_consumer.subscribe.assert_called_once_with(['test-topic'])
        self.assertEqual(self.mock_consumer.poll.call_count, 2)

    def test_consumer_error_message(self):
        # Create a mock message with an error
        mock_msg = MagicMock(spec=Message)
        mock_error = MagicMock(spec=KafkaError)
        mock_error.code.return_value = KafkaError._PARTITION_EOF
        mock_msg.error.return_value = mock_error
        mock_msg.topic.return_value = 'test-topic'
        mock_msg.partition.return_value = 0
        
        # Set up consumer to return one error message then None
        self.mock_consumer.poll.side_effect = [mock_msg, None]
        
        # Call consumer
        consume_course_completed_events(self.mock_consumer, 'test-topic', timeout=0.1, max_empty_polls=1)
        
        # Verify consumer handled the error and continued
        self.mock_consumer.subscribe.assert_called_once_with(['test-topic'])
        self.assertEqual(self.mock_consumer.poll.call_count, 2)

if __name__ == '__main__':
    unittest.main()
