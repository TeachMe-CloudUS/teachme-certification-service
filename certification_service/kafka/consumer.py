from confluent_kafka import Consumer, KafkaError, Producer, KafkaException
import json
import signal
import threading
from certification_service.course_cert_utils import certify_student
from certification_service.logger import logger
from certification_service.models.student_course_data  import Student_Course_Data
import os

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
        student_course_data = Student_Course_Data.from_json(event_data)
        # Proceed with certification or further processing
        certify_student(student_course_data)

    except json.JSONDecodeError:
        logger.error("Failed to decode message: %s", msg.value())
    except ValueError  as value_error:
        logger.error(f"Failed to decode Kafka event: {value_error}")
    except KeyError as e:
        logger.error(f"Missing key in Kafka event data: {e}")
        logger.error(f"Event data: {event_data}")
    except Exception as e:
        logger.exception("Error processing Kafka event: %s", e)

def consume_course_completed_events(consumer, timeout=1.0):
    """Consume course completed events from Kafka."""
    topics = ['student-service.course.completed']
    consumer.subscribe(topics)
    logger.info("Consumer started and subscribed to topics: %s", topics)
    
    empty_poll_count = 0

    try:
        while running:  # Use the running flag for graceful shutdown
            msg = consumer.poll(timeout)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

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
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVER'),
        'group.id': 'certification-group',
        'auto.offset.reset': 'earliest'
    }
    return Consumer(conf)

def consumer_thread_func():
    """Function to run in the consumer thread"""
    consumer = create_consumer()
    try:
        consume_course_completed_events(consumer)
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
