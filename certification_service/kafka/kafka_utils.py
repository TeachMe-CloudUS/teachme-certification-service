import json
from confluent_kafka import Producer, Consumer
from datetime import datetime
from dataclasses import dataclass, asdict


def kafka_producer_config():
    config = {
        'bootstrap.servers': 'localhost:9092',  
        'client.id': 'certification_service_producer',  
        'acks': 'all'  
    }
    return Producer(config)

def kafka_consumer_config():
    config = {
        'bootstrap.servers': 'localhost:9092',  
        'group.id': 'certification_service_group',  
        'auto.offset.reset': 'earliest'  
    }
    return Consumer(config)

def create_topic_name(service: str, entity: str, action: str, version: str = 'v1') -> str:
    """
    Create a standardized Kafka topic name.
    
    Args:
        service (str): The service name (e.g., 'certification_service')
        entity (str): The entity type (e.g., 'certificate')
        action (str): The action being performed (e.g., 'generated')
        version (str, optional): The version of the topic. Defaults to 'v1'.
    
    Returns:
        str: A formatted Kafka topic name
    """
    return f"{service}.{entity}.{action}.{version}"

@dataclass
class StudentUpdateEvent:
    student_id: str
    user_id: str
    phone_number: str
    
    @staticmethod
    def from_json(data: dict):
        """Convert a dictionary (e.g., from Kafka message) to a StudentUpdateEvent object."""
        return StudentUpdateEvent(
            student_id=data["studentId"],
            user_id=data["userId"],
            phone_number=data["phoneNumber"]
        )

    def to_json(self):
        """Convert the StudentUpdateEvent object to a JSON-compatible dictionary."""
        return json.dumps({
            "studentId": self.student_id,
            "userId": self.user_id,
            "phoneNumber": self.phone_number,
        })

@dataclass
class CourseCompletedEvent:
    student_id: str
    user_id: str
    course_id: str
    enrollment_date: str  # ISO-8601 format string

    @staticmethod
    def from_json(data: dict):
        """Convert JSON dictionary to a CourseCompletedEvent object."""
        return CourseCompletedEvent(
            student_id=data["studentId"],
            user_id=data["userId"],
            course_id=data["courseId"],
            enrollment_date=data["enrollmentDate"]
        )

    def to_json(self):
        """Convert the event to a JSON-compatible dictionary."""
        return json.dumps(asdict(self))


@dataclass
class KafkaEvent:
    service: str
    entity: str
    action: str
    version: str = None

    def to_dict(self):
        """Convert the event to a dictionary."""
        return {
            "service": self.service,
            "entity": self.entity,
            "action": self.action,
            "version": self.version
        }

    def to_json(self):
        """Convert the event to a JSON string."""
        return json.dumps(self.to_dict())
