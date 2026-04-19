from app import app, db
import os

def reset_database():
    print("Starting database reset...")
    
    # Path to the database file
    # Based on app.py config: 'sqlite:///db.sqlite'
    # And the existence of 'instance/db.sqlite'
    db_paths = [
        os.path.join('instance', 'db.sqlite'),
        'db.sqlite'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Deleted old database: {db_path}")
            except Exception as e:
                print(f"Error deleting {db_path}: {e}")

    with app.app_context():
        db.create_all()
        print("Successfully recreated database with the new schema (including 'email' column).")

if __name__ == "__main__":
    reset_database()
