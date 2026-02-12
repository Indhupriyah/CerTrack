#!/usr/bin/env python3
"""
CerTrack - Email reminder system.

Sends notifications:
- 1 day before registration deadline
- 5 days before expected completion
- 1 day before expected completion

Usage: python scripts/reminders.py
Cron: 0 9 * * * cd /path/to/CerTrack && python scripts/reminders.py
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def already_sent(user_id, cert_id, reminder_type, target_date):
    """Check if we already sent this reminder."""
    from app.models.reminder_log import ReminderLog
    return ReminderLog.query.filter_by(
        user_id=user_id,
        certification_id=cert_id,
        reminder_type=reminder_type,
        target_date=target_date
    ).first() is not None


def log_reminder(user_id, cert_id, reminder_type, target_date):
    """Record that we sent a reminder."""
    from app.models.reminder_log import ReminderLog
    from app import db
    log = ReminderLog(
        user_id=user_id,
        certification_id=cert_id,
        reminder_type=reminder_type,
        target_date=target_date
    )
    db.session.add(log)
    db.session.commit()


def send_email(app, to_email, subject, body):
    """Send email via Flask-Mail."""
    if not app.config.get("MAIL_USERNAME") or not app.config.get("MAIL_PASSWORD"):
        print(f"[SKIP] Mail not configured. Would send to {to_email}: {subject}")
        return False
    try:
        from flask_mail import Message
        from app import mail
        msg = Message(subject=subject, recipients=[to_email], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send to {to_email}: {e}")
        return False


def run_reminders():
    from app import create_app, db
    from app.models.certification import Certification
    from app.models.reminder_log import ReminderLog

    app = create_app()
    with app.app_context():
        db.create_all()  # Ensure reminder_logs table exists
        today = date.today()

        certs = Certification.query.filter(
            Certification.status.in_(["upcoming", "in_progress"])
        ).all()

        sent = 0
        for c in certs:
            user = c.user
            if not user or not user.email:
                continue

            # 1 day before registration deadline
            if c.registration_deadline:
                target = c.registration_deadline
                if today + timedelta(days=1) == target:
                    if not already_sent(user.id, c.id, "reg_1d", target):
                        body = f"Hi {user.display_name or 'there'},\n\n"
                        body += f"Reminder: '{c.name}' registration deadline is tomorrow ({target.strftime('%b %d, %Y')}).\n\n"
                        body += "Log in to CerTrack to view details."
                        if send_email(app, user.email, f"CerTrack: Register by tomorrow - {c.name}", body):
                            log_reminder(user.id, c.id, "reg_1d", target)
                            sent += 1

            # 5 days before expected completion
            if c.expected_completion and c.status != "completed":
                target = c.expected_completion
                if today + timedelta(days=5) == target:
                    if not already_sent(user.id, c.id, "completion_5d", target):
                        body = f"Hi {user.display_name or 'there'},\n\n"
                        body += f"Reminder: '{c.name}' expected completion is in 5 days ({target.strftime('%b %d, %Y')}).\n\n"
                        body += "Log in to CerTrack to track your progress."
                        if send_email(app, user.email, f"CerTrack: 5 days left - {c.name}", body):
                            log_reminder(user.id, c.id, "completion_5d", target)
                            sent += 1

                # 1 day before expected completion
                if today + timedelta(days=1) == target:
                    if not already_sent(user.id, c.id, "completion_1d", target):
                        body = f"Hi {user.display_name or 'there'},\n\n"
                        body += f"Reminder: '{c.name}' expected completion is tomorrow ({target.strftime('%b %d, %Y')}).\n\n"
                        body += "Log in to CerTrack to update your status."
                        if send_email(app, user.email, f"CerTrack: Complete tomorrow - {c.name}", body):
                            log_reminder(user.id, c.id, "completion_1d", target)
                            sent += 1

        print(f"Reminders sent: {sent}")


if __name__ == "__main__":
    run_reminders()
