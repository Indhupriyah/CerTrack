"""Add username column to users table if missing (SQLite-safe)."""
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
        print(f"SQLite DB not found. If using PostgreSQL, run: ALTER TABLE users ADD COLUMN username VARCHAR(80) UNIQUE;")
        return
    conn = sqlite3.connect(db_path)
    cur = conn.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cur.fetchall()]
    if "username" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN username VARCHAR(80)")
        conn.commit()
        try:
            conn.execute("CREATE UNIQUE INDEX ix_users_username ON users (username)")
            conn.commit()
        except sqlite3.OperationalError:
            pass
        print("Added users.username column.")
    else:
        print("Column username already exists.")
    conn.close()

if __name__ == "__main__":
    main()
