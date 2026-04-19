from app import app, db
import os

def repair_db():
    print("Repairing database...")
    with app.app_context():
        # This will create missing tables without deleting existing data
        db.create_all()
    print("Database tables verified.")

if __name__ == "__main__":
    repair_db()
