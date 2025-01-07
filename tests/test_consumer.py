import pytest
from unittest.mock import MagicMock
from confluent_kafka import Consumer, KafkaError, KafkaException
from certification_service.course_cert_utils import certify_student
from certification_service.models.student_course_data import Student_Course_Data
from your_module import consume_course_completed_events, process_event, signal_handler


# Mocking logger to prevent actual logging during tests
@pytest.fixture(autouse=True)
def mock_logger(monkeypatch):
    mock_logger = MagicMock()
    monkeypatch.setattr("your_module.logger", mock_logger)
    return mock_logger


# Test the signal handler
def test_signal_handler():
    global running
    running = True
    signal_handler(15, None)  # SIGTERM signal (signal number 15)
    assert not running


# Test process_event function with valid input
def test_process_event_valid():
    msg = MagicMock()
    msg.value.return_value = '{"student_id": 1, "course_id": "course_101", "status": "completed"}'

    # Mocking the method certify_student
    with pytest.raises(Exception):  # Mock exception if needed
        process_event(msg)
        
    # Check if the certify_student method is called
    student_course_data = Student_Course_Data.from_json(
        {"student_id": 1, "course_id": "course_101", "status": "completed"}
    )
    assert certify_student.called
    assert certify_student.call_args[0][0] == student_course_data


# Test the consume_course_completed_events function
@pytest.mark.parametrize("msg_value, expected_exception", [
    ('{"student_id": 1, "course_id": "course_101", "status": "completed"}', None),
    ('invalid_message', json.JSONDecodeError),
])
def test_consume_course_completed_events(msg_value, expected_exception, monkeypatch):
    consumer_mock = MagicMock()
    consumer_mock.poll.return_value = MagicMock(value=msg_value)
    consumer_mock.commit.return_value = None

    if expected_exception:
        with pytest.raises(expected_exception):
            consume_course_completed_events(consumer_mock, timeout=1)
    else:
        consume_course_completed_events(consumer_mock, timeout=1)
        consumer_mock.commit.assert_called_once()

