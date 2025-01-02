import unittest
import signal
import threading
import time
from unittest.mock import MagicMock, patch
from certification_service.kafka.producer import producer, start_producer, close_producer
from certification_service.kafka.consumer import start_consumer
from confluent_kafka import KafkaError, Message

class TestGracefulShutdown(unittest.TestCase):
    @patch('certification_service.kafka.producer.running', True)
    @patch('certification_service.kafka.consumer.running', True)
    def setUp(self):
        pass

    def test_producer_shutdown(self):
        # Mock the producer
        mock_producer = MagicMock()
        with patch('certification_service.kafka.producer.producer', mock_producer):
            # Start producer
            start_producer()
            
            # Simulate SIGTERM
            signal.raise_signal(signal.SIGTERM)
            
            # Give time for signal handler
            time.sleep(0.1)
            
            # Test producer cleanup
            close_producer()
            
            # Verify flush was called
            mock_producer.flush.assert_called_once()

    def test_consumer_shutdown(self):
        # Mock the consumer
        mock_consumer = MagicMock()
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = b'{"studentId": "123", "userId": "456"}'
        mock_consumer.poll.side_effect = [mock_msg, None]  # Return one message then None
        
        with patch('certification_service.kafka.consumer.create_consumer', return_value=mock_consumer):
            # Start consumer
            consumer_thread = start_consumer()
            
            # Give time for consumer to start
            time.sleep(0.1)
            
            # Simulate SIGTERM
            signal.raise_signal(signal.SIGTERM)
            
            # Give time for signal handler
            time.sleep(0.1)
            
            # Wait for consumer thread to finish
            consumer_thread.join(timeout=1)
            
            # Verify cleanup calls
            mock_consumer.commit.assert_called()
            mock_consumer.close.assert_called_once()

    def test_producer_flush_with_remaining_messages(self):
        # Mock the producer with remaining messages
        mock_producer = MagicMock()
        mock_producer.flush.return_value = 5  # 5 messages not delivered
        
        with patch('certification_service.kafka.producer.producer', mock_producer):
            # Test producer cleanup
            close_producer()
            
            # Verify flush was called with timeout
            mock_producer.flush.assert_called_once_with(timeout=5)

    def test_consumer_commit_error_handling(self):
        # Mock the consumer with commit error
        mock_consumer = MagicMock()
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = b'{"studentId": "123", "userId": "456"}'
        mock_consumer.poll.side_effect = [mock_msg, None]
        mock_consumer.commit.side_effect = KafkaError(KafkaError.INVALID_CONFIG)
        
        with patch('certification_service.kafka.consumer.create_consumer', return_value=mock_consumer):
            # Start consumer
            consumer_thread = start_consumer()
            
            # Give time for consumer to start
            time.sleep(0.1)
            
            # Simulate SIGTERM
            signal.raise_signal(signal.SIGTERM)
            
            # Give time for signal handler
            time.sleep(0.1)
            
            # Wait for consumer thread to finish
            consumer_thread.join(timeout=1)
            
            # Verify error handling
            mock_consumer.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
