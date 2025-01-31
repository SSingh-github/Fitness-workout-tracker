
from werkzeug.security import generate_password_hash
from bson import ObjectId
from datetime import datetime

class Exercise:
    def __init__(self, name, duration, description, user_id):
        self.name = name
        self.duration = duration
        self.description = description
        self.user_id = ObjectId(user_id)

    def to_dict(self):
        return {
            "name": self.name,
            "duration": self.duration,
            "description": self.description,
            "user_id": self.user_id
        }


class Comment:
    def __init__(self, text, workout_id):
        self.text = text
        self.workout_id = ObjectId(workout_id)
        self.date_time = datetime.utcnow()

    def to_dict(self):
        return {
            "text": self.text,
            "workout_id": self.workout_id,
            "date_time": self.date_time
        }


class Workout:
    def __init__(self, user_id, name, status, start_date_time):
        self.user_id = ObjectId(user_id)
        self.name = name
        self.status = status  # "pending" or "done"
        self.start_date_time = datetime.strptime(start_date_time, "%Y-%m-%d %H:%M:%S")  # User-provided time
        self.exercises = []  # List of exercise ObjectIds
        self.comments = []  # List of comment ObjectIds

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "status": self.status,
            "start_date_time": self.start_date_time,
            "exercises": self.exercises,
            "comments": self.comments
        }


class User:
    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = generate_password_hash(password)
    
    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "password": self.password
        }