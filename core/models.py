from .extensions import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """User model for the application"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    morning_grog = db.Column(db.Integer, default=20)
    peak_duration = db.Column(db.Integer, default=90)
    trough_duration = db.Column(db.Integer, default=20)
    cycles = db.Column(db.Integer, default=4)

    daily_records = db.relationship(
        "UserDailyRecord", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.name} - {self.email}>"


class UserDailyRecord(db.Model):
    """Daily log with wake time and optional HRV"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    wake_time = db.Column(db.Time, nullable=False)
    hrv = db.Column(db.Float)

    cycle_events = db.relationship(
        "UserCycleEvent",
        backref="user_daily_record",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<UserDailyRecord {self.date}>"


class UserCycleEvent(db.Model):
    """Model for individual cycle events"""

    id = db.Column(db.Integer, primary_key=True)
    user_daily_record_id = db.Column(
        db.Integer, db.ForeignKey("user_daily_record.id"), nullable=False
    )
    event_type = db.Column(db.String(50), nullable=False)  # e.g., 'peak', 'trough'
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f"<UserCycleEvent {self.event_type} {self.start_time}–{self.end_time}>"
