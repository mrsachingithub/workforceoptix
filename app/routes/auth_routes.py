from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app import db
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle API login or Form login
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_verified and user.role != 'Admin': # Admins (seeded) are verified by default usually, but let's assume seeded ones are.
                 # Actually, for seeded admin, we should ensure they are verified.
                 # For normal users, check flag.
                 return jsonify({"msg": "Account pending verification by Manager."}), 403
            
            access_token = create_access_token(identity=str(user.id))
            resp = jsonify({'login': True, 'token': access_token})
            set_access_cookies(resp, access_token)
            return resp, 200
        return jsonify({"msg": "Bad username or password"}), 401

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or Email already exists', 'danger')
            return redirect(url_for('auth.register'))
            
        # Default is_verified is False
        new_user = User(username=username, email=email, is_verified=False)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please wait for Manager approval.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Logic to send email would go here (Mocked)
        flash(f'If an account exists for {email}, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')

@auth_bp.route('/profile')
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200
