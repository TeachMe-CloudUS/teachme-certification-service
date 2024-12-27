import unittest
from certification_service.app import create_app
from unittest.mock import patch, MagicMock

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

if __name__ == '__main__':
    unittest.main()
