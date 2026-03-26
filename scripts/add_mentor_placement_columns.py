"""Add is_mentor and is_placement columns to users table if missing."""
import os
import sqlite3

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_uri = os.environ.get("DATABASE_URL", "sqlite:///certrack.db")
    if db_uri.startswith("sqlite:///"):
        path = db_uri.replace("sqlite:///", "")
        if os.path.isabs(path):
            db_path = path
        else:
            db_path = os.path.join(root, path)
            if not os.path.isfile(db_path):
                db_path = os.path.join(root, "instance", path)
    else:
        db_path = os.path.join(root, "instance", "certrack.db")
    if not os.path.isfile(db_path):
        print("SQLite DB not found. If using PostgreSQL, run: ALTER TABLE users ADD COLUMN is_mentor BOOLEAN DEFAULT 0; ALTER TABLE users ADD COLUMN is_placement BOOLEAN DEFAULT 0;")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cur.fetchall()]
    for col, default in [("is_mentor", 0), ("is_placement", 0)]:
        if col not in cols:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} BOOLEAN DEFAULT {default}")
            conn.commit()
            print(f"Added users.{col}")
        else:
            print(f"Column {col} already exists.")
    conn.close()

if __name__ == "__main__":
    main()
