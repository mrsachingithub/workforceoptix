from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from app import db
from app.models import Employee, User

employee_bp = Blueprint('employee', __name__, url_prefix='/employees')

@employee_bp.route('/')
@jwt_required()
def list_employees():
    employees = Employee.query.all()
    return render_template('employees/list.html', employees=employees)

@employee_bp.route('/add', methods=['GET', 'POST'])
@jwt_required()
def add_employee():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        designation = request.form.get('designation')
        skills = request.form.get('skills')
        
        if Employee.query.filter_by(email=email).first():
            flash('Employee with this email already exists', 'danger')
            return redirect(url_for('employee.add_employee'))
            
        new_emp = Employee(
            name=name, 
            email=email, 
            mobile=mobile,
            designation=designation, 
            skills=skills
        )
        db.session.add(new_emp)
        db.session.commit()
        
        # Auto-Link to User if exists
        user = User.query.filter_by(email=email).first()
        if user:
            user.employee_id = new_emp.id
            db.session.commit()
            flash('New employee added and linked to existing user account!', 'success')
        else:
            flash('New employee added successfully!', 'success')
            
        return redirect(url_for('employee.list_employees'))
        
    return render_template('employees/add.html')

@employee_bp.route('/<int:id>')
@jwt_required()
def view_employee(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employees/view.html', employee=employee)
