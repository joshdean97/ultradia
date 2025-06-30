from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date, time

from core.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(30), nullable=False)

    peak_duration = db.Column(db.Integer, default=90)
    trough_duration = db.Column(db.Integer, default=20)
    morning_grog = db.Column(db.Integer, default=30)
    cycles = db.Column(db.Integer, default=3)

    is_admin = db.Column(db.Boolean, default=False)

    def latest_record(self):
        return (
            UserDailyRecord.query.filter_by(user_id=self.id)
            .order_by(UserDailyRecord.date.desc())
            .first()
        )

    @property
    def latest_hrv(self):
        r = self.latest_record()
        return r.hrv if r else None

    @property
    def latest_rhr(self):
        r = self.latest_record()
        return r.rhr if r else None

    @property
    def last_sleep_duration(self):
        r = self.latest_record()
        return r.sleep_duration if r else None

    @property
    def latest_mood(self):
        r = self.latest_record()
        return r.mood if r else None

    def latest_record(self):
        return (
            UserDailyRecord.query.filter_by(user_id=self.id)
            .order_by(UserDailyRecord.date.desc())
            .first()
        )

    def get_baseline(self, metric: str, days: int = 7):
        """
        Generic baseline calculator for a given metric (e.g. 'hrv', 'rhr', 'sleep_duration')
        Excludes today's record.
        """
        valid_metrics = {"hrv", "rhr", "sleep_duration"}
        if metric not in valid_metrics:
            raise ValueError(f"Unsupported metric: {metric}")

        records = (
            UserDailyRecord.query.filter_by(user_id=self.id)
            .filter(getattr(UserDailyRecord, metric).isnot(None))
            .order_by(UserDailyRecord.date.desc())
            .limit(days + 1)
            .all()
        )

        today = date.today()
        recent = [getattr(r, metric) for r in records if r.date != today]

        if not recent or len(recent) < 2:
            return None

        return round(sum(recent) / len(recent), 2)

    def calculate_vital_index(self):
        records = (
            UserDailyRecord.query.filter_by(user_id=self.id)
            .order_by(UserDailyRecord.date.desc())
            .limit(7)
            .all()
        )
        valid = [r for r in records if r.hrv and r.hrv > 30]
        if len(valid) < 2:
            return None

        today_record = valid[0]
        past = valid[1:]
        baseline = sum(r.hrv for r in past) / len(past)
        today_hrv = today_record.hrv
        index = round((today_hrv / baseline) * 100)

        return {
            "vital_index": index,
            "today_hrv": today_hrv,
            "baseline_hrv": round(baseline, 2),
            "status": (
                "above baseline"
                if index > 110
                else "below baseline" if index < 90 else "baseline"
            ),
        }


class UserDailyRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    date = db.Column(db.Date, default=date.today, nullable=False)
    wake_time = db.Column(db.Time, default=datetime.now().time, nullable=False)
    hrv = db.Column(db.Integer)
    rhr = db.Column(db.Integer)
    sleep_duration = db.Column(db.Float)
    mood = db.Column(db.String, nullable=True)

    # cycle_events = db.relationship(
    #     "UserCycleEvent",
    #     backref="user_daily_record",
    #     lazy=True,
    #     cascade="all, delete-orphan",
    # )

    def as_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "wake_time": self.wake_time.isoformat(),
            "hrv": self.hrv,
            "rhr": self.rhr,
            "sleep_duration": self.sleep_duration,
            "mood": self.mood,
        }


class UserCycleEvent(db.Model):
    """Model for individual cycle events"""

    id = db.Column(db.Integer, primary_key=True)
    user_daily_record_id = db.Column(
        db.Integer, db.ForeignKey("user_daily_record.id"), nullable=False
    )
    event_type = db.Column(db.String(50), nullable=False)  # e.g., 'peak', 'trough'
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    record = db.relationship("UserDailyRecord", backref="events", lazy=True)

    def __repr__(self):
        return f"<UserCycleEvent {self.event_type} {self.start_time}–{self.end_time}>"


class Leads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, default=datetime.now())
