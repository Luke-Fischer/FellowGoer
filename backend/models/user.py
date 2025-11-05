from models import db
from utils.auth import hash_password, check_password


class User(db.Model):
    """User model for storing user information"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password = hash_password(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password(password, self.password)

    def to_dict(self):
        """Convert user object to dictionary (excludes password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
