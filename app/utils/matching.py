from app.models import Employee, Project

def find_matching_employees(project_id, min_match_percent=50):
    project = Project.query.get(project_id)
    if not project or not project.required_skills:
        return []

    req_skills = [s.strip().lower() for s in project.required_skills.split(',')]
    matches = []
    
    # Check all bench employees first? Or all available?
    # Let's check all Bench and Partially Utilized
    candidates = Employee.query.filter(Employee.availability_status.in_(['Bench', 'Partially Utilized'])).all()
    
    for emp in candidates:
        if not emp.skills:
            continue
        
        emp_skills = [s.strip().lower() for s in emp.skills.split(',')]
        matched_skills = set(req_skills).intersection(set(emp_skills))
        
        match_percent = (len(matched_skills) / len(req_skills)) * 100
        
        if match_percent >= min_match_percent:
            matches.append({
                'employee': emp,
                'match_percent': round(match_percent, 1),
                'matched_skills': ', '.join(matched_skills)
            })
            
    # Sort by match percent desc
    matches.sort(key=lambda x: x['match_percent'], reverse=True)
    return matches

def find_projects_for_employee(employee_id, min_match_percent=50):
    employee = Employee.query.get(employee_id)
    if not employee or not employee.skills:
        return []

    emp_skills = [s.strip().lower() for s in employee.skills.split(',')]
    matches = []
    
    # Check all Active Projects
    active_projects = Project.query.filter_by(status='Active').all()
    
    for proj in active_projects:
        if not proj.required_skills:
            continue
            
        req_skills = [s.strip().lower() for s in proj.required_skills.split(',')]
        matched_skills = set(emp_skills).intersection(set(req_skills))
        
        match_percent = (len(matched_skills) / len(req_skills)) * 100
        
        if match_percent >= min_match_percent:
            matches.append({
                'project': proj,
                'match_percent': round(match_percent, 1),
                'matched_skills': ', '.join(matched_skills)
            })
            
    matches.sort(key=lambda x: x['match_percent'], reverse=True)
    return matches
