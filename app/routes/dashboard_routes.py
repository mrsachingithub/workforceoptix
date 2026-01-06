from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Employee, Allocation
from sqlalchemy import func
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@jwt_required()
def index():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Role Based Redirect/Render
    if user.role == 'Admin':
        return admin_dashboard(user)
    elif user.role == 'Employee':
        return employee_dashboard(user)
    else:
        return render_template('dashboard/index.html', user=user, stats={})

def admin_dashboard(user):
    # Stats Calculation
    total_employees = Employee.query.count()
    bench_count = Employee.query.filter_by(availability_status='Bench').count()
    
    # Pending Approvals
    pending_users = User.query.filter_by(is_verified=False).all()
    # Customers (Active Projects details)
    active_projects = db.session.query(Allocation.project_id).distinct().all() 
    # This is rough, normally we need a Customer model, but let's list Projects for now as "Customers/Projects"
    
    today = datetime.today().date()
    total_allocated_hours = db.session.query(func.sum(Allocation.allocated_hours)).filter(Allocation.end_date >= today).scalar() or 0
    
    total_capacity = total_employees * 40
    utilization_rate = 0
    if total_capacity > 0:
        utilization_rate = (total_allocated_hours / total_capacity) * 100
    
    stats = {
        'total_employees': total_employees,
        'bench_count': bench_count,
        'utilization_rate': round(utilization_rate, 1)
    }
    
    return render_template('dashboard/admin.html', user=user, stats=stats, pending_users=pending_users)

def employee_dashboard(user):
    # Get my allocations
    if not user.employee_profile:
        return render_template('dashboard/employee.html', user=user, allocations=[])
        
    emp_id = user.employee_profile.id
    today = datetime.today().date()
    today = datetime.today().date()
    my_allocations = Allocation.query.filter(Allocation.employee_id == emp_id).order_by(Allocation.end_date.desc()).all()
    
    return render_template('dashboard/employee.html', user=user, allocations=my_allocations)

@dashboard_bp.route('/link_profile', methods=['POST'])
@jwt_required()
def link_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    email = request.form.get('email')
    
    if not email:
        flash('Please enter an email address.', 'danger')
        return redirect(url_for('dashboard.index'))
        
    employee = Employee.query.filter_by(email=email).first()
    
    if employee:
        user.employee_id = employee.id
        db.session.commit()
        flash(f'Successfully linked to employee profile: {employee.name}', 'success')
    else:
        flash('No employee found with that email address.', 'danger')
        
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/approve_user/<int:user_id>')
@jwt_required()
def approve_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if current_user.role != 'Admin':
        return redirect(url_for('dashboard.index'))
        
    user_to_verify = User.query.get(user_id)
    if user_to_verify:
        user_to_verify.is_verified = True
        
        # Auto-Link Employee Profile if email matches
        matching_employee = Employee.query.filter_by(email=user_to_verify.email).first()
        if matching_employee:
            user_to_verify.employee_id = matching_employee.id
            flash(f"User approved and linked to Employee: {matching_employee.name}", "success")
        else:
            flash(f"User approved. No matching employee profile found for {user_to_verify.email}", "warning")
            
        db.session.commit()
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/contact')
def contact():
    return render_template('contact.html')

@dashboard_bp.route('/')
def home():
    return render_template('index.html')
