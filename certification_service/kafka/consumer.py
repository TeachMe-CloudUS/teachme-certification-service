from confluent_kafka import Consumer, KafkaError, Producer
import json
import signal
import threading
from certification_service.course_cert_utils import certify_student
from certification_service.logger import logger
from certification_service.kafka.events import create_topic_name

running = True
consumer_thread = None

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global running
    logger.info("Shutdown signal received, initiating graceful shutdown...")
    running = False

def process_event(msg):
    try:
        event_data = json.loads(msg.value().decode('utf-8'))
        logger.info("Event received: %s", event_data)

        student_id = event_data.get('studentId')
        user_id = event_data.get('userId')
        course_id = event_data.get('courseId')

        if not isinstance(student_id, str) or not isinstance(user_id, str) or not isinstance(course_id, str):
            logger.warning("Invalid event data: %s", event_data)
            return

        certify_student(student_id, user_id, course_id)
        logger.info("Successfully certified student: %s (User ID: %s) for course: %s", student_id, user_id, course_id)

    except json.JSONDecodeError:
        logger.error("Failed to decode message: %s", msg.value())
    except Exception as e:
        logger.exception("Error processing event: %s", e)

def consume_course_completed_events(consumer, topics, timeout=1.0, max_empty_polls=10):
    """Consume course completed events from Kafka."""
    consumer.subscribe([topics])
    logger.info("Consumer started and subscribed to topics: %s", topics)
    
    empty_poll_count = 0

    try:
        while running:  # Use the running flag for graceful shutdown
            msg = consumer.poll(timeout)
            if msg is None:
                empty_poll_count += 1
                if empty_poll_count >= max_empty_polls:
                    logger.info("No messages received after multiple polls. Exiting consumer.")
                    break
                continue

            empty_poll_count = 0  # Reset on successful poll

            if msg.error():
                if msg.error().code() == KafkaError.PARTITION_EOF:
                    logger.debug("End of partition reached for %s [%d]", msg.topic(), msg.partition())
                    continue
                else:
                    logger.error("Consumer error: %s", msg.error())
                    break

            process_event(msg)

            try:
                consumer.commit(message=msg)
                logger.info("Message committed: %s", msg.offset())
            except Exception as e:
                logger.error("Failed to commit message: %s", e)

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user.")
    finally:
        try:
            # Commit final offsets
            consumer.commit(asynchronous=False)
            logger.info("Final offsets committed")
        except Exception as e:
            logger.error(f"Error committing final offsets: {e}")
        
        consumer.close()
        logger.info("Consumer closed successfully")

def create_consumer():
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'notification-group',
        'auto.offset.reset': 'earliest'
    }
    return Consumer(conf)

def consumer_thread_func():
    """Function to run in the consumer thread"""
    consumer = create_consumer()
    topic = create_topic_name("certification", "course", "completed")
    
    try:
        consume_course_completed_events(consumer, topic)
    except Exception as e:
        logger.error(f"Error in consumer: {e}")
    finally:
        logger.info("Shutting down consumer...")

def start_consumer():
    """Initialize and start the consumer with graceful shutdown."""
    global consumer_thread
    
    # Only register signal handlers in the main thread
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Start consumer in a separate thread
    consumer_thread = threading.Thread(target=consumer_thread_func)
    consumer_thread.start()
    
    return consumer_thread
