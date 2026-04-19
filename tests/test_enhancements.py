import unittest
import os
from datetime import datetime

from app import app, db
from models import User, LoginLog

class EnhancementTests(unittest.TestCase):
    def setUp(self):
        # Use a temporary SQLite database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_db.sqlite'
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
            # Create a test user
            test_user = User(email='test@example.com', password='testpass')
            # Hash password as in registration flow
            from werkzeug.security import generate_password_hash
            test_user.password = generate_password_hash('testpass')
            db.session.add(test_user)
            db.session.commit()
            self.user_id = test_user.id

    def tearDown(self):
        # Clean up the test database file
        with app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists('test_db.sqlite'):
            os.remove('test_db.sqlite')

    def test_login_logging(self):
        # Perform login POST
        response = self.app.post('/login', data={'email': 'test@example.com', 'password': 'testpass'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Verify a LoginLog entry was created
        with app.app_context():
            logs = LoginLog.query.filter_by(user_id=self.user_id).all()
            self.assertTrue(len(logs) >= 1, "LoginLog entry not found after login")

    def test_new_activity_routes(self):
        # Access English words activity
        resp_en = self.app.get('/learning/english_words')
        self.assertEqual(resp_en.status_code, 200)
        # Access Respectful learner activity
        resp_res = self.app.get('/learning/respectful')
        self.assertEqual(resp_res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
