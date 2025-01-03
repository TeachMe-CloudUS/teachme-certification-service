import unittest
from certification_service.app import create_app
from unittest.mock import patch, MagicMock
from certification_service.models.student_course_data import Student_Course_Data
from certification_service.kafka.consumer import consume_course_completed_events

class TestAppInitialization(unittest.TestCase):
    @patch('threading.Thread')
    @patch('certification_service.database.db_connection.init_mongodb')  # Mock MongoDB initialization
    @patch('certification_service.kafka.consumer.start_consumer')  # Mock Kafka consumer start
    @patch('certification_service.kafka.producer.send_certification_notification')  # Mock producer function
    def test_app_creation(self, mock_producer, mock_consumer, mock_db_init, mock_thread):
        # Mock successful database initialization
        mock_db_init.return_value = MagicMock()
        
        # Create the app
        app = create_app()

        # Ensure the app is created without errors
        self.assertIsNotNone(app)
        
        # Check if the thread was started with the consumer
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()

        # Check if producer function is available
        mock_producer.assert_not_called()  # Ensure that producer's send_certification_notification is not called during app creation

        # Test using Student_Course_Data
        student_course_data = Student_Course_Data()
        self.assertIsInstance(student_course_data, Student_Course_Data)

    @patch('certification_service.kafka.consumer.Consumer')
    def test_consumer_message_commit(self, MockConsumer):
        # Mock the consumer
        mock_consumer_instance = MagicMock()
        MockConsumer.return_value = mock_consumer_instance
        
        # Mock the consumer's poll and commit
        mock_message = MagicMock()
        mock_message.value.return_value = '{"student_id": 1, "course_id": 101}'
        mock_consumer_instance.poll.return_value = mock_message
        mock_consumer_instance.commit.return_value = None  # Mock successful commit
        
        # Run the consumer logic
        consume_course_completed_events(mock_consumer_instance)
        
        # Check that the commit was called with the message
        mock_consumer_instance.commit.assert_called_once_with(message=mock_message)

if __name__ == '__main__':
    unittest.main()
