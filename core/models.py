from .extensions import db


class User(db.Model):
    """User model for the application"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    morning_grog = db.Column(db.Integer, default=20)
    peak_duration = db.Column(db.Integer, default=90)
    trough_duration = db.Column(db.Integer, default=20)
    cycles = db.Column(db.Integer, default=4)

    def __repr__(self):
        return f"<User {self.name} - {self.email}>"


class UserDailyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    wake_time = db.Column(db.Time, nullable=False)
    hrv = db.Column(db.Float)  # Optional for biometrics

    user = db.relationship("User", backref=db.backref("daily_records", lazy=True))

    def __repr__(self):
        return f"<UserDailyRecord {self.date} - Cycle {self.cycle}>"


class UserCycleEvent(db.Model):
    """Model for individual cycle events"""

    id = db.Column(db.Integer, primary_key=True)
    user_daily_record_id = db.Column(
        db.Integer, db.ForeignKey("user_daily_record.id"), nullable=False
    )
    event_type = db.Column(db.String(50), nullable=False)  # e.g., 'peak', 'trough'
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    user_daily_record = db.relationship(
        "UserDailyRecord", backref=db.backref("cycle_events", lazy=True)
    )

    def __repr__(self):
        return (
            f"<UserCycleEvent {self.event_type} - {self.start_time} to {self.end_time}>"
        )
