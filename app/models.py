from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='Employee') # Admin, Manager, Employee
    is_verified = db.Column(db.Boolean, default=False)
    # Link to Employee profile if applicable
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'employee_id': self.employee_id
        }

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20))
    designation = db.Column(db.String(64))
    skills = db.Column(db.Text) # Stored as comma-separated string for simplicity
    # Status: 'Bench', 'Active', 'Partially Utilized'
    availability_status = db.Column(db.String(20), default='Bench') 
    
    # Relationships
    user = db.relationship('User', backref='employee_profile', uselist=False)
    allocations = db.relationship('Allocation', backref='employee', lazy='dynamic')

    @property
    def last_allocation_end_date(self):
        # Get the latest end date from allocations
        last_alloc = self.allocations.order_by(Allocation.end_date.desc()).first()
        if last_alloc:
            return last_alloc.end_date
        return None

    @property
    def bench_days(self):
        if self.availability_status != 'Bench':
            return 0
        
        last_end = self.last_allocation_end_date
        if last_end:
            delta = datetime.today().date() - last_end
            return max(0, delta.days)
        # If never allocated but on bench, assume since creation? 
        # For now, return 0 or handle separately.
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'designation': self.designation,
            'skills': self.skills,
            'availability_status': self.availability_status,
            'bench_days': self.bench_days
        }

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    client_name = db.Column(db.String(64), nullable=False)
    required_skills = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active') # Active, Completed
    
    allocations = db.relationship('Allocation', backref='project', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'client_name': self.client_name,
            'required_skills': self.required_skills,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status
        }

class Allocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    allocated_hours = db.Column(db.Integer, default=40) # Hours per week
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'project_id': self.project_id,
            'allocated_hours': self.allocated_hours,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None
        }
