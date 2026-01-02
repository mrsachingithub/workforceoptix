from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required
from app.models import Employee, Allocation
from app.utils.matching import find_projects_for_employee
from datetime import datetime

bench_bp = Blueprint('bench', __name__, url_prefix='/bench')

@bench_bp.route('/')
@jwt_required()
def list_bench():
    # Sort by bench days descending
    bench_employees = Employee.query.filter_by(availability_status='Bench').all()
    # Python sort as bench_days is a property
    bench_employees.sort(key=lambda x: x.bench_days, reverse=True)
    
    return render_template('bench/list.html', bench_employees=bench_employees)

@bench_bp.route('/match/<int:employee_id>')
@jwt_required()
def match_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    matches = find_projects_for_employee(employee_id)
    return render_template('bench/matches.html', employee=employee, matches=matches)
