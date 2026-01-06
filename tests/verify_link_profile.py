import unittest
import sys
import os

# Adjust path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Employee

class TestConfig(object):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing of forms
    SECRET_KEY = 'test-secret'
    JWT_SECRET_KEY = 'test-jwt-secret'

class VerifyLinkProfile(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create a user (Employee Role)
        self.user = User(username='rashmika', email='rashmika@example.com', role='Employee', is_verified=True)
        self.user.set_password('password')
        db.session.add(self.user)
        
        # Create an employee profile (Not linked yet)
        self.employee = Employee(name='Rashmika V', email='rashmika@workforce.com', designation='Developer', availability_status='Bench')
        db.session.add(self.employee)
        
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_link_profile_success(self):
        # 1. Login
        login_resp = self.client.post('/auth/login', json={ # Assuming login is JSON based on previous file, but let's check. 
            # Wait, dashboard routes use @jwt_required().
            # Need to get access token first.
            'username': 'rashmika', 
            'password': 'password'
        })
        
        self.assertEqual(login_resp.status_code, 200)
        token = login_resp.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. Link Profile
        response = self.client.post('/link_profile', data={
            'email': 'rashmika@workforce.com'
        }, headers=headers, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 3. Verify Database
        user_in_db = User.query.get(self.user.id)
        self.assertIsNotNone(user_in_db.employee_id)
        self.assertEqual(user_in_db.employee_id, self.employee.id)
        self.assertIn(b'Successfully linked to employee profile', response.data)

    def test_link_profile_fail_invalid_email(self):
        # Login
        login_resp = self.client.post('/auth/login', json={'username': 'rashmika', 'password': 'password'})
        token = login_resp.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}

        response = self.client.post('/link_profile', data={
            'email': 'wrong@email.com'
        }, headers=headers, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        user_in_db = User.query.get(self.user.id)
        self.assertIsNone(user_in_db.employee_id)
        self.assertIn(b'No employee found', response.data)

if __name__ == '__main__':
    unittest.main()
