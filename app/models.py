
from werkzeug.security import generate_password_hash

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