import json
from dataclasses import dataclass, asdict
from datetime import datetime

class StudentUpdateEvent:
    student_id: str
    user_id: str
    
    @staticmethod
    def from_json(data: dict):
        """Convert a dictionary (e.g., from Kafka message) to a StudentUpdateEvent object."""
        return StudentUpdateEvent(
            student_id=data["studentId"],
            user_id=data["userId"],
        )

    def to_json(self):
        """Convert the StudentUpdateEvent object to a JSON-compatible dictionary."""
        return json.dumps({
            "studentId": self.student_id,
            "userId": self.user_id,
           
        })

@dataclass
class CourseCompletedEvent:
    student_id: str
    student_userId: str
    student_name: str
    student_surname: str
    student_email: str
    course_id: str
    course_name: str
    course_description: str
    course_duration: str
    course_level: str
    completionDate:str  # ISO-8601 format string
    

    @staticmethod
    def from_json(data: dict):
        """Convert JSON dictionary to a CourseCompletedEvent object."""
        return CourseCompletedEvent(
            student_id=data["student"]["id"],
            student_userId=data["student"]["userId"],
            student_name=data["student"]["name"],
            student_surname=data["student"]["surname"],
            student_email=data["student"]["email"],
            course_id=data["course"]["courseId"],
            course_name=data["course"]["courseName"],
            course_description=data["course"]["courseDescription"],
            course_duration=data["course"]["courseDuration"],
            course_level=data["course"]["level"],
            completionDate=data["completionDate"]           
        )

    def to_json(self):
        """Convert the event to a JSON-compatible dictionary."""
        return json.dumps(asdict(self))


@dataclass
class KafkaEvent:
    service: str
    entity: str
    action: str
    version: str = "v1"  # Default to 'v1'

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