import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'certrack.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN file_path VARCHAR(255)")
        print("file_path column added to messages table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("file_path column already exists.")
        else:
            print(f"Error adding column: {e}")
            
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN file_name VARCHAR(255)")
        print("file_name column added to messages table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("file_name column already exists.")
        else:
            print(f"Error adding column: {e}")
            
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN is_read BOOLEAN DEFAULT 0")
        print("is_read column added to messages table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("is_read column already exists.")
        else:
            print(f"Error adding column: {e}")
            
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN year_of_study VARCHAR(50)")
        print("year_of_study column added to users table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("year_of_study column already exists.")
        else:
            print(f"Error adding column: {e}")
            
    conn.commit()
    conn.close()
else:
    print(f"Database file not found at {db_path}")
