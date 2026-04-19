from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, UTC

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True) # Explicit username
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    activities = db.relationship('ActivityLog', backref='user', lazy=True)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)
    details = db.Column(db.Text) # Changed from String(500) to Text for larger reports
    metadata_json = db.Column(db.Text) # New: To store JSON breakdown reports
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False) # Simplification: Storing as string YYYY-MM-DD
    time = db.Column(db.String(10), nullable=False)
    notes = db.Column(db.Text) # Rich text notes supported
    status = db.Column(db.String(20), default='Scheduled') # Scheduled, Completed, Cancelled
    homework = db.Column(db.String(200)) # Linked module ID or title


class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class DailyGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, default=lambda: datetime.now(UTC).date())

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    note = db.Column(db.Text)
    stress_level = db.Column(db.Integer, default=1) # 1-5
    sentiment_score = db.Column(db.Float, nullable=True) # NLP generated score
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class SensoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    noise_level = db.Column(db.Float)
    brightness = db.Column(db.Float)
    trigger_detected = db.Column(db.Boolean, default=False)
    details = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class BehaviorPrediction(db.Model):
    """Stores informal wellness labels from in-app heuristics—not clinical assessments."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    predicted_state = db.Column(db.String(100))  # User-facing wellness snapshot label
    confidence = db.Column(db.Float)
    reasoning = db.Column(db.Text)
    remedy_suggestion = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class UserBadge(db.Model):
    """Stores gamification achievements/badges for users."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_desc = db.Column(db.String(255))
    icon = db.Column(db.String(50)) # e.g. emoji or font-awesome class
    earned_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


