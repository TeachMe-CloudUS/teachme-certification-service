from kafka_utils import kafka_producer_config, kafka_consumer_config, KafkaEvent, create_topic_name
import json
from app import CourseCompletedEvent, certify_student, update_certificates_for_student
from kafka_utils import StudentUpdateEvent
from confluent_kafka import KafkaError

# Kafka configuration
producer = kafka_producer_config()
consumer = kafka_consumer_config()

# Topic creation
topic_name = create_topic_name('certification_service', 'certificate', 'generated', 'v1')

# Produce a message
def produce_event(producer, topic, key, event: KafkaEvent):
    try:
        producer.produce(topic, key=key, value=event.to_json())
        producer.flush()
    except Exception as e:
        print(f"Error producing event: {e}")


# Consume messages
def consume_course_completed_events(consumer, topics, timeout=1.0):
    """Consumes messages from Kafka and processes them as CourseCompletedEvent."""
    consumer.subscribe(topics)
    while True:
        msg = consumer.poll(timeout)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error consuming message: {msg.error()}")
                break

        # Process the message
        try:
            event_data = json.loads(msg.value())
            event = CourseCompletedEvent.from_json(event_data)
            print(f"Consumed event: {event}")

            # Certifaction - creation
            success = certify_student(
                student_id=event.student_id,
                course_id=event.course_id,
                user_id=event.user_id,
                enrollment_date=event.enrollment_date
            )
            #if success:
               # print(f"Certificate created successfully for student {event.student_id}.")
            #else:
              #  print(f"Failed to create certificate for student {event.student_id}.")
                
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

def consume_student_update_events(consumer, topics, timeout=1.0):
    """Consumes messages from Kafka and processes them as StudentUpdateEvent."""
    consumer.subscribe(topics)
    while True:
        msg = consumer.poll(timeout)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error consuming message: {msg.error()}")
                break

        # Process the message
        try:
            event_data = json.loads(msg.value())
            event = StudentUpdateEvent.from_json(event_data)
            print(f"Consumed event: {event}")

            # Call the method to update certificates
            update_certificates_for_student(
                student_id=event.student_id,
                user_id=event.user_id
            )
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")


# Produce Events
# Topic name for certificate generation
topic_certificate_generated = create_topic_name('certification_service', 'certificate', 'generated', 'v1')

# Topic name for certificate update
topic_certificate_updated = create_topic_name('certification_service', 'certificate', 'updated', 'v1')




