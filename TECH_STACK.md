# CerTrack – Technology Stack & Architecture

## Overview

CerTrack is a browser-based student certification and event planning platform built as a responsive web application. This document lists the tools, stacks, technologies, modules, and algorithms used, along with their purpose.

---

## Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.x | Primary programming language for backend logic, APIs, and automation |
| **Flask** | 3.0.0 | Web framework – routing, request handling, app factory pattern |
| **Flask-SQLAlchemy** | 3.1.1 | ORM for database operations – models, queries, migrations |
| **Flask-Login** | 0.6.3 | Session-based authentication – login, logout, protected routes |
| **Flask-WTF** | 1.2.1 | Form handling and CSRF protection |
| **Flask-Mail** | 0.9.1 | Email sending for deadline reminders |
| **Werkzeug** | 3.0.1 | WSGI utilities – password hashing, request/response handling |
| **python-dotenv** | 1.0.0 | Load environment variables from `.env` |
| **email-validator** | 2.1.0 | Validate email addresses on signup |

---

## Database

| Technology | Purpose |
|------------|---------|
| **SQLite** | Default development database (file-based, no setup) |
| **PostgreSQL** | Production database (optional via `DATABASE_URL`) |
| **psycopg2-binary** | PostgreSQL adapter (install when using PostgreSQL) |

**Schema:** User, Certification, Resource, Event, Analytics, ReminderLog tables with foreign keys and indexes.

---

## Frontend Stack

| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure and semantics |
| **CSS3** | Styling, responsive layout, dark mode, animations |
| **JavaScript (Vanilla)** | Theme toggle, mobile menu, Kanban drag-and-drop, calendar rendering |
| **Jinja2** | Server-side templating (included with Flask) |
| **Google Fonts (Inter)** | Typography |

---

## Application Modules

| Module | Path | Purpose |
|--------|------|---------|
| **Auth** | `app/routes/auth.py`, `app/utils/auth.py` | Login, signup, logout, password hashing, OAuth placeholders |
| **Main** | `app/routes/main.py` | Landing page, dashboard, file uploads |
| **Certifications** | `app/routes/certifications.py` | CRUD, Kanban, calendar, resources, certificate upload |
| **Events** | `app/routes/events.py` | CRUD for hackathons, workshops, etc. |
| **Portfolio** | `app/routes/portfolio.py` | Private and public portfolio views |
| **API** | `app/routes/api.py` | Calendar events JSON for certifications and events |
| **Models** | `app/models/` | User, Certification, Resource, Event, Analytics, ReminderLog |
| **Reminders** | `scripts/reminders.py` | Scheduled email notifications for deadlines |

---

## Algorithms & Logic

| Algorithm / Logic | Location | Purpose |
|-------------------|----------|---------|
| **Password hashing (scrypt)** | `app/utils/auth.py` | Secure storage of passwords |
| **Random slug generation** | `app/utils/auth.py` | Unique public portfolio URLs |
| **Date-based reminder checks** | `scripts/reminders.py` | Match `today + N days` to deadline dates |
| **Duplicate reminder prevention** | `scripts/reminders.py`, `ReminderLog` | Avoid sending same email twice |
| **Monthly completion trend** | `app/routes/main.py` | Aggregate completions per month (last 6 months) |
| **Skill aggregation** | `app/routes/main.py`, portfolio | Count skill tags from completed certifications |
| **Upcoming deadlines filter** | `app/routes/main.py` | Certifications/events within next 14 days |
| **Kanban status update** | `app/routes/certifications.py` | PATCH API for drag-and-drop status change |
| **Analytics sync on completion** | `app/routes/certifications.py` | Increment `certifications_completed` when moved to Completed |

---

## DevOps & Tooling

| Tool | Purpose |
|------|---------|
| **Cron** | Schedule `scripts/reminders.py` daily (e.g. 9 AM) |
| **Gunicorn / uWSGI** | Production WSGI server (recommended over Flask dev server) |
| **.env** | Store `SECRET_KEY`, `DATABASE_URL`, `MAIL_*` secrets |

---

## Data Flow Summary

```
User Request → Flask Route → Model (SQLAlchemy) → Database
                    ↓
              Jinja2 Template → HTML Response

Calendar: /api/calendar/events → JSON (certifications + events)

Reminders: Cron → scripts/reminders.py → Flask-Mail → SMTP → User Email
```

---

## File Structure

```
CerTrack/
├── app/                 # Flask application
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # Blueprint route handlers
│   └── utils/           # Auth helpers
├── templates/           # Jinja2 HTML templates
├── static/              # CSS, JS, assets
├── scripts/             # CLI scripts (reminders)
├── run.py               # Development server entry point
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variable template
```
