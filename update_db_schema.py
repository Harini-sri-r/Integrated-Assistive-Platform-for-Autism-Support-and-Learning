import app
from models import db

with app.app.app_context():
    try:
        db.create_all()
        print("Database schema updated successfully.")
    except Exception as e:
        print(f"Error updating database: {e}")
