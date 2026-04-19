import sqlite3
import os

db_path = os.path.join('instance', 'db.sqlite')
if not os.path.exists(db_path):
    db_path = 'db.sqlite'

print(f"Targeting database at: {db_path}")

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("Deleted existing database file.")
    except Exception as e:
        print(f"Failed to delete: {e}. It might be locked by a running app.")

# Now we need to recreate it. Instead of importing app (which might have locks), 
# we just let the next run of the app create it. 
# BUT we want to be SURE it has the right columns.
