import json
from dataclasses import dataclass, asdict

@dataclass
class Student_Course_Data:
    student_id: str = None
    student_userId: str = None
    student_name: str = None
    student_surname: str = None
    student_email: str = None
    course_id: str = None
    course_name: str = None
    course_description: str = None
    course_duration: str = None
    course_level: str = None
    completionDate: str = None

    def __post_init__(self):
        """
        Validate the data after initialization.
        This method is automatically called by dataclasses after __init__
        """
        self._validate()

    def _validate(self):
        """
        Validate the event data.
        Raises ValueError if critical fields are missing or invalid.
        """
        required_fields = ['student_id', 'course_id']
        for field in required_fields:
            value = getattr(self, field)
            if not value or value.strip() == "": 
                raise ValueError(f"Missing or empty required field: {field}")

        optional_fields = ['student_userId', 'student_name', 'student_surname', 'student_email', 'course_name', 'course_description', 'course_duration', 'course_level', 'completionDate']
        for field in optional_fields:
            value = getattr(self, field)
            if value is not None and value.strip() == "": 
                raise ValueError(f"Field {field} cannot be an empty string if provided.")

    @staticmethod
    def from_json(data: dict):
        """Convert JSON dictionary to a Student_Course_Data object."""
        return Student_Course_Data(
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