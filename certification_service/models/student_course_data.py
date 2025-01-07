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
            value = str(getattr(self, field))
            if not value or value.strip() == "": 
                raise ValueError(f"Missing or empty required field: {field}")

        optional_fields = ['student_userId', 'student_name', 'student_surname', 'student_email', 'course_name', 'course_description', 'course_duration', 'course_level', 'completionDate']
        for field in optional_fields:
            value = str(getattr(self, field))
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
            course_id=data["course"]["id"],
            course_name=data["course"]["name"],
            course_description=data["course"]["description"],
            course_duration=data["course"]["duration"],
            course_level=data["course"]["level"],
            completionDate=data["completionDate"]           
        )

    def to_json(self):
        """Convert the event to a JSON-compatible dictionary."""
        return json.dumps(asdict(self))

    @classmethod
    def from_db_student_course_data(cls, certificate_dict):
        """Create a Student_Course_Data object from a certificate dictionary."""
        certificate_dict = certificate_dict.copy()
        try:
            del certificate_dict['blob_link']
        except KeyError:
            pass
        # Mapping between dictionary keys and class attribute names
        attribute_mapping = {
            'student_id': 'student_id',
            'name': 'student_name',
            'surname': 'student_surname', 
            'email': 'student_email',
            'course_id': 'course_id',
            'course_name': 'course_name',
            'course_description': 'course_description',
            'course_duration': 'course_duration',
            'course_level': 'course_level',
            'completionDate': 'completionDate'
        }
        
        # Create a new dictionary with mapped keys
        mapped_dict = {}
        for dict_key, class_key in attribute_mapping.items():
            if dict_key in certificate_dict:
                mapped_dict[class_key] = certificate_dict[dict_key]
        
        # Create and return the Student_Course_Data object
        return cls(**mapped_dict)