from app import app, db
import sqlite3
import os

def diagnose():
    with app.app_context():
        # Get the engine and its URI
        uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Configured URI: {uri}")
        
        # Determine the practical path
        if uri.startswith('sqlite:///'):
            db_file = uri[10:]
            # If it's relative, it might be in instance/ if not absolute
            print(f"Extracted file name: {db_file}")
            
            # Check project root
            if os.path.exists(db_file):
                print(f"Found at project root: {os.path.abspath(db_file)}")
                path_to_check = db_file
            elif os.path.exists(os.path.join(app.instance_path, db_file)):
                 print(f"Found in instance folder: {os.path.abspath(os.path.join(app.instance_path, db_file))}")
                 path_to_check = os.path.join(app.instance_path, db_file)
            else:
                print("Database file NOT FOUND in root or instance.")
                return

            # Check schema via sqlite3 directly
            try:
                conn = sqlite3.connect(path_to_check)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(user)")
                columns = cursor.fetchall()
                print("\nColumns in 'user' table:")
                for col in columns:
                    print(f" - {col[1]} ({col[2]})")
                conn.close()
            except Exception as e:
                print(f"Error reading SQLite schema: {e}")

if __name__ == "__main__":
    diagnose()
