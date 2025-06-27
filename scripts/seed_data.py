# ultradia/scripts/seed_data.py

import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


from datetime import date, timedelta, time
from core.extensions import db
from core.models import User, UserDailyRecord
from core import create_app
import random


# Init app + context
app = create_app()
app.app_context().push()

# Get or create test user
user = User.query.filter_by(email="josh@test.com").first()
if not user:
    user = User(email="josh@test.com")
    db.session.add(user)
    db.session.commit()

# Remove existing daily records
UserDailyRecord.query.filter_by(user_id=user.id).delete()

# Add 10 days of mock records
for i in range(10, 0, -1):
    record_date = date.today() - timedelta(days=i)
    record = UserDailyRecord(
        user_id=user.id,
        date=record_date,
        wake_time=time(6, 45),
        hrv=random.randint(55, 85),
        rhr=random.randint(48, 62),
        sleep_duration=round(random.uniform(6.5, 8.5), 2),
        mood="🙂",  # or any emoji string
    )
    db.session.add(record)

db.session.commit()
print("✅ Seeded 10 days of mock data.")
