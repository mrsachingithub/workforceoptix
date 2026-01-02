from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from app import db
from app.models import Allocation, Employee, Project
from datetime import datetime

allocation_bp = Blueprint('allocation', __name__, url_prefix='/allocations')

def update_employee_status(employee_id):
    employee = Employee.query.get(employee_id)
    if not employee:
        return
        
    # seamless calc
    total_hours = 0
    # Filter for active allocations only? Prompt implies current status. 
    # Let's assume all allocations in table are "current" or filter by date.
    # For simplicity, let's sum all "active" allocations (where end_date >= today).
    today = datetime.today().date()
    
    active_allocs = Allocation.query.filter(Allocation.employee_id == employee_id, Allocation.end_date >= today).all()
    
    for alloc in active_allocs:
        total_hours += alloc.allocated_hours
        
    utilization = (total_hours / 40) * 100
    
    if utilization >= 80:
        employee.availability_status = 'Fully Utilized'
    elif utilization >= 40:
        employee.availability_status = 'Partially Utilized'
    else:
        employee.availability_status = 'Bench'
        
    db.session.commit()

@allocation_bp.route('/')
@jwt_required()
def list_allocations():
    allocations = Allocation.query.all()
    return render_template('allocations/list.html', allocations=allocations)

@allocation_bp.route('/add', methods=['GET', 'POST'])
@jwt_required()
def add_allocation():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        project_id = request.form.get('project_id')
        allocated_hours = int(request.form.get('allocated_hours'))
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        new_alloc = Allocation(employee_id=employee_id, project_id=project_id, 
                               allocated_hours=allocated_hours, start_date=start_date, end_date=end_date)
        db.session.add(new_alloc)
        db.session.commit()
        
        # Update Status
        update_employee_status(employee_id)
        
        flash('Allocation added successfully', 'success')
        return redirect(url_for('allocation.list_allocations'))
        
    employees = Employee.query.all()
    projects = Project.query.filter_by(status='Active').all()
    return render_template('allocations/add.html', employees=employees, projects=projects)
