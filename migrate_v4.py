import sqlite3
import os

db_file = 'instance/platform_v3.db'

if not os.path.exists(db_file):
    print(f"Database {db_file} not found. Ensure the app is initialized.")
    exit()

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    print("Migrating database for V4 upgrades...")

    # 1. Add sentiment_score to journal_entry
    try:
        cursor.execute("ALTER TABLE journal_entry ADD COLUMN sentiment_score FLOAT")
        print(" - Added 'sentiment_score' to journal_entry.")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print(" - 'sentiment_score' already exists.")
        else:
            print(f" - Error adding 'sentiment_score': {e}")

    # 2. Create user_badge table
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_badge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_name VARCHAR(100) NOT NULL,
                badge_desc VARCHAR(255),
                icon VARCHAR(50),
                earned_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
        ''')
        print(" - Created 'user_badge' table.")
    except Exception as e:
        print(f" - Error creating 'user_badge': {e}")

    conn.commit()
    print("Migration complete!")

except Exception as e:
    print(f"Migration failed: {e}")
finally:
    conn.close()
