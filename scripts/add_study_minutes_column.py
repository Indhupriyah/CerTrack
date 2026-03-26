"""Add study_minutes column to analytics table if missing (SQLite-safe)."""
import os
import sqlite3

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_uri = os.environ.get("DATABASE_URL", "sqlite:///certrack.db")
    if db_uri.startswith("sqlite:///"):
        # sqlite:///certrack.db -> path relative to app root or absolute
        path = db_uri.replace("sqlite:///", "")
        if os.path.isabs(path):
            db_path = path
        else:
            db_path = os.path.join(root, path)
            if not os.path.isfile(db_path):
                db_path = os.path.join(root, "instance", path)
    else:
        db_path = os.path.join(root, "certrack.db")
        if not os.path.isfile(db_path):
            db_path = os.path.join(root, "instance", "certrack.db")
    if not os.path.isfile(db_path):
        print(f"SQLite DB not found at {db_path}. If using PostgreSQL, run: ALTER TABLE analytics ADD COLUMN study_minutes INTEGER DEFAULT 0;")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.execute("PRAGMA table_info(analytics)")
    cols = [row[1] for row in cur.fetchall()]
    if "study_minutes" not in cols:
        conn.execute("ALTER TABLE analytics ADD COLUMN study_minutes INTEGER DEFAULT 0")
        conn.commit()
        print("Added analytics.study_minutes column.")
    else:
        print("Column study_minutes already exists.")
    conn.close()

if __name__ == "__main__":
    main()
