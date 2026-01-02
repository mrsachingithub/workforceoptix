from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from app import db
from app.models import Project
from datetime import datetime

project_bp = Blueprint('project', __name__, url_prefix='/projects')

@project_bp.route('/')
@jwt_required()
def list_projects():
    projects = Project.query.all()
    return render_template('projects/list.html', projects=projects)

@project_bp.route('/add', methods=['GET', 'POST'])
@jwt_required()
def add_project():
    if request.method == 'POST':
        name = request.form.get('name')
        client_name = request.form.get('client_name')
        required_skills = request.form.get('required_skills')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        new_project = Project(
            name=name, 
            client_name=client_name, 
            required_skills=required_skills,
            start_date=start_date,
            end_date=end_date,
            status='Active'
        )
        db.session.add(new_project)
        db.session.commit()
        
        flash('Project added successfully', 'success')
        return redirect(url_for('project.list_projects'))
        
    return render_template('projects/add.html')

@project_bp.route('/<int:id>')
@jwt_required()
def view_project(id):
    project = Project.query.get_or_404(id)
    return render_template('projects/view.html', project=project)
