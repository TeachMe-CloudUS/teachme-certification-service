from confluent_kafka import Consumer, KafkaError
import json
from certification_service.cert_management import certify_student
from certification_service.logger import logger
from certification_service.kafka.events import create_topic_name

def process_event(msg):
    try:
        event_data = json.loads(msg.value().decode('utf-8'))
        logger.info("Event received: %s", event_data)

        student_id = event_data.get('studentId')
        user_id = event_data.get('userId')

        if not isinstance(student_id, str) or not isinstance(user_id, str):
            logger.warning("Invalid event data: %s", event_data)
            return

        certify_student(student_id, user_id)
        logger.info("Successfully certified student: %s (User ID: %s)", student_id, user_id)

    except json.JSONDecodeError:
        logger.error("Failed to decode message: %s", msg.value())
    except Exception as e:
        logger.exception("Error processing event: %s", e)

def consume_course_completed_events(consumer, topics, timeout=1.0):
    """Consume course completed events from Kafka."""
    consumer.subscribe([topics])
    logger.info("Consumer started and subscribed to topics: %s", topics)
    try:
        while True:
            msg = consumer.poll(timeout)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
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
        consumer.close()
        logger.info("Consumer closed.")
        

# Initial setup
def create_consumer ():
    conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'notification-group',
    'auto.offset.reset': 'earliest'
}
    return Consumer(conf)

def start_consumer():
    """Initialize and start the consumer."""
    consumer = create_consumer()
    course_completed_topic = create_topic_name("student_service", "course", "completed")
    consume_course_completed_events(consumer, course_completed_topic)


