from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Will store hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with saved trips
    saved_trips = db.relationship('SavedTrip', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class SavedTrip(db.Model):
    """Model for saved itineraries"""
    __tablename__ = 'saved_trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    days = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.String(20), nullable=False)
    trip_type = db.Column(db.String(20), nullable=False)
    itinerary_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavedTrip {self.destination} for {self.user_id}>'