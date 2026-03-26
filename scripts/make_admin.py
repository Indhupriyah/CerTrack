"""Set is_admin=True for a user by email. Usage: python -m scripts.make_admin user@example.com"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app, db
from app.models.user import User

def main():
    email = (sys.argv[1] or "").strip().lower()
    if not email:
        print("Usage: python -m scripts.make_admin user@example.com")
        sys.exit(1)
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"No user with email {email}")
            sys.exit(1)
        user.is_admin = True
        db.session.commit()
        print(f"Done. {email} is now an admin.")

if __name__ == "__main__":
    main()
