# UltraDia API 🚀

A Flask-based API backend for **UltraDia**, the ultradian rhythm tracker that helps users work with their biology—not against it.

## 🌱 Overview

UltraDia is a productivity and wellness platform that uses ultradian rhythm tracking, biometric feedback, and user personalization to help people maximize their energy and focus.

This repository contains the backend application built with Flask, SQLAlchemy, and Flask-Login. It includes:

- User authentication and profile management
- Ultradian rhythm cycle generation
- HRV (Heart Rate Variability) based energy potential analysis
- Health check integrations
- Blueprinted modular structure

## 🔧 Features

- ✅ User Registration & Login (hashed passwords, session-based)
- 🧠 Ultradian Cycle Generator
- 🫀 HRV-based Energy Potential Index (Vital Score)
- 📊 Daily Record Logging
- 🔁 Fully extensible via Blueprints
- 🌐 CORS-ready API for frontend integration

## 🗂 Project Structure

```
core/
├── __init__.py        # Flask app factory
├── auth.py            # Auth routes
├── users.py           # User management
├── records.py         # Daily record logging
├── rhythms.py         # Ultradian rhythm endpoints
├── vital.py           # Energy potential based on HRV
├── models.py          # SQLAlchemy models
├── functions.py       # Cycle calculation logic
├── extensions.py      # Database, CORS, migration setup
├── config.py          # Environment-based configuration
health-check.py        # SNS-based health check notifier
wsgi.py                # Production entrypoint
app.py                 # Development entrypoint
```

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ultradia-backend.git
cd ultradia-backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your `.env` file:

```bash
# .env
SECRET_KEY=your-secret
DB_URI=sqlite:///ultradia.db
HEALTHCHECK_ARN=your-sns-topic-arn
```

5. Run the app (development):

```bash
python app.py
```

6. Run with Gunicorn (production):

```bash
gunicorn wsgi:app
```

## 🔌 API Endpoints

| Method | Endpoint                   | Description                            |
|--------|----------------------------|----------------------------------------|
| GET    | `/api/health`              | Health check                           |
| POST   | `/api/auth/register`       | Register a new user                    |
| POST   | `/api/auth/login`          | Login and start session                |
| POST   | `/api/auth/logout`         | Logout user                            |
| GET    | `/api/users/me`            | Get current user profile               |
| PUT    | `/api/users/<id>`          | Update user profile                    |
| DELETE | `/api/users/<id>`          | Delete user account                    |
| POST   | `/api/records/create`      | Create a daily record                  |
| POST   | `/api/ultradian`           | Generate ultradian cycles              |
| GET    | `/api/energy-potential`    | Get calculated energy potential (HRV)  |

## 🧪 Testing the Health Check

```bash
python health-check.py
```

This will perform a GET request to `/api/health` and publish to SNS if unhealthy.

## 🧠 About

This backend powers the UltraDia app — a mission-driven tool to align productivity with biology. It's part of a broader suite under **Neurostacker**.

## ✅ To Do

- [ ] Add bio data input throughwearables
- [ ] Include sleep data in energy potential
- [ ] Link up /leads to RDS database

## 🛡 License

MIT License. See `LICENSE` for details.

---

> Built with ❤️ by the UltraDia team.
