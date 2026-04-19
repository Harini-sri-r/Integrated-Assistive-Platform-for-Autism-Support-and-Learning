import sqlite3
import os

db_file = 'instance/platform_v3.db'

if not os.path.exists(db_file):
    print(f"Database {db_file} not found. Skipping migration.")
    exit()

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

try:
    print("Migrating 'appointment' table...")
    
    # 1. Add 'status' column
    try:
        cursor.execute("ALTER TABLE appointment ADD COLUMN status VARCHAR(20) DEFAULT 'Scheduled'")
        print(" - Added 'status' column.")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e):
             print(" - 'status' column already exists.")
        else:
             print(f" - Error adding 'status': {e}")

    # 2. Add 'homework' column
    try:
        cursor.execute("ALTER TABLE appointment ADD COLUMN homework VARCHAR(200)")
        print(" - Added 'homework' column.")
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e):
             print(" - 'homework' column already exists.")
        else:
             print(f" - Error adding 'homework': {e}")
             
    # 3. Add 'notes' column if missing (it was added earlier but let's be safe)
    try:
        cursor.execute("ALTER TABLE appointment ADD COLUMN notes TEXT")
        print(" - Added 'notes' column.")
    except sqlite3.OperationalError as e:
        # Expected if it already exists
        pass

    conn.commit()
    print("Migration complete.")

except Exception as e:
    print(f"Migration failed: {e}")
finally:
    conn.close()
