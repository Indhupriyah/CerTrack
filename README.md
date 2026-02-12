# CerTrack

A browser-based student certification and technical event planning platform. Track certifications, manage events (hackathons, workshops, contests), and build a verified achievement portfolio.

## Features

- **Authentication**: Email/password signup & login, OAuth placeholders (Google, GitHub)
- **Dashboard**: Summary cards, monthly goals, completion %, study streaks
- **Certifications**: Kanban view, calendar view, add/edit/delete, resource library, certificate upload
- **Events**: Track hackathons, workshops, coding contests with registration & result dates
- **Portfolio**: Completed certifications grid, skill cloud, public shareable URL
- **Responsive**: Mobile bottom nav, tablet collapsed sidebar, desktop full layout
- **Dark mode**: Toggle persisted in localStorage

## Tech Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL (or SQLite for dev)
- **Frontend**: HTML, CSS, vanilla JavaScript

## Setup

### 1. Clone & install

```bash
cd CerTrack
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env: set SECRET_KEY, DATABASE_URL (or leave for SQLite)
```

### 3. Run

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000).

### PostgreSQL (production)

```bash
# Create DB
createdb certrack

# .env
DATABASE_URL=postgresql://user:password@localhost:5432/certrack
```

## Project Structure

```
CerTrack/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── config.py
│   ├── models/          # User, Certification, Resource, Event, Analytics
│   ├── routes/          # auth, main, certifications, events, portfolio, api
│   └── utils/
├── templates/
├── static/
│   ├── css/
│   └── js/
├── scripts/
│   └── reminders.py     # Background reminder placeholder
├── run.py
├── requirements.txt
└── README.md
```

## Reminders

The `scripts/reminders.py` script sends email notifications to each user's registered email:
- **1 day before** registration deadline
- **5 days before** expected completion
- **1 day before** expected completion

Configure `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env`. For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833). Run daily via cron:

```
0 9 * * * cd /path/to/CerTrack && python scripts/reminders.py
```

## Database migrations

For new columns (e.g. `location` on events), run:

```bash
python scripts/add_location_column.py
```

## Tech stack

See [TECH_STACK.md](TECH_STACK.md) for tools, technologies, modules, and algorithms used.

## License

MIT
