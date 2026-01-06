import unittest
import sys
import os
from datetime import datetime, date

# Adjust path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Employee, Project, Allocation

class TestConfig(object):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'
    JWT_SECRET_KEY = 'test-jwt-secret'

class VerifyAllocationActions(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create Admin
        self.admin = User(username='admin', email='admin@test.com', role='Admin')
        self.admin.set_password('password')
        db.session.add(self.admin)

        # Create Employee
        self.employee = Employee(name='Test Emp', email='emp@test.com', availability_status='Bench')
        db.session.add(self.employee)

        # Create Project
        self.project = Project(name='Test Proj', client_name='Client', status='Active')
        db.session.add(self.project)
        
        db.session.commit()

        # Login and get token
        resp = self.client.post('/auth/login', json={'username': 'admin', 'password': 'password'})
        self.token = resp.get_json()['token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_edit_allocation(self):
        # 1. Create Allocation
        active_alloc = Allocation(
            employee_id=self.employee.id, 
            project_id=self.project.id, 
            allocated_hours=20, 
            start_date=date(2025, 1, 1), 
            end_date=date(2026, 1, 1)
        )
        db.session.add(active_alloc)
        db.session.commit()
        
        alloc_id = active_alloc.id

        # 2. Edit Allocation (Increase hours)
        resp = self.client.post(f'/allocations/edit/{alloc_id}', data={
            'employee_id': self.employee.id,
            'project_id': self.project.id,
            'allocated_hours': 40,
            'start_date': '2025-01-01',
            'end_date': '2026-06-01'
        }, headers=self.headers, follow_redirects=True)
        
        self.assertEqual(resp.status_code, 200)

        # 3. Verify DB update
        updated_alloc = Allocation.query.get(alloc_id)
        self.assertEqual(updated_alloc.allocated_hours, 40)
        self.assertEqual(str(updated_alloc.end_date), '2026-06-01')
        
        # 4. Verify Employee Status (Should be Fully Utilized)
        updated_emp = Employee.query.get(self.employee.id)
        # Note: logic relies on update_employee_status running.
        # 40 hours = 100% utilization -> Fully Utilized
        self.assertEqual(updated_emp.availability_status, 'Fully Utilized')

    def test_delete_allocation(self):
        # 1. Create Allocation
        alloc = Allocation(
            employee_id=self.employee.id, 
            project_id=self.project.id, 
            allocated_hours=40, 
            start_date=date(2025, 1, 1), 
            end_date=date(2026, 1, 1)
        )
        db.session.add(alloc)
        # Manually set status to Fully Utilized initially
        self.employee.availability_status = 'Fully Utilized'
        db.session.commit()
        
        alloc_id = alloc.id

        # 2. Delete Allocation
        resp = self.client.post(f'/allocations/delete/{alloc_id}', headers=self.headers, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # 3. Verify DB Deletion
        deleted_alloc = Allocation.query.get(alloc_id)
        self.assertIsNone(deleted_alloc)

        # 4. Verify Employee Status (Should revert to Bench)
        updated_emp = Employee.query.get(self.employee.id)
        self.assertEqual(updated_emp.availability_status, 'Bench')

if __name__ == '__main__':
    unittest.main()
