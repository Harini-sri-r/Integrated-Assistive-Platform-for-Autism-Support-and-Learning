from app import app, db
from models import JournalEntry, SensoryLog, BehaviorPrediction

def init_tables():
    with app.app_context():
        # This will create any missing tables defined in models.py
        # without affecting existing tables if they already exist.
        db.create_all()
        print("New tables (JournalEntry, SensoryLog, BehaviorPrediction) integrated successfully.")

if __name__ == "__main__":
    init_tables()
