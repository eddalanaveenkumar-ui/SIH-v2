from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import mongo
from bson import ObjectId

portal_bp = Blueprint('portal', __name__)


@portal_bp.route('/')
def portal_home():
    """Secret portal homepage - only for teacher/HOD registration"""
    return render_template('portal/portal_home.html')


@portal_bp.route('/signup', methods=['GET', 'POST'])
def portal_signup():
    """Secret signup portal for teachers and HODs only"""
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role == 'teacher':
            return redirect(url_for('teacher.teacher_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        name = request.form.get('name', '')
        secret_code = request.form.get('secret_code', '')

        # Validate passwords match
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('portal/portal_signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('portal/portal_signup.html')

        # Check if user already exists
        if User.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('portal/portal_signup.html')

        # Validate secret codes
        if user_type == 'teacher' and secret_code != "TEACHER123":
            flash('Invalid teacher secret code', 'danger')
            return render_template('portal/portal_signup.html')

        if user_type == 'admin' and secret_code != "ADMIN123":
            flash('Invalid admin secret code', 'danger')
            return render_template('portal/portal_signup.html')

        # Create user
        try:
            user_id = User.create_user(email, password, user_type, name)
            flash('Registration successful! You can now login from the main portal.', 'success')
            return redirect(url_for('portal.portal_login'))
        except Exception as e:
            flash('Error creating user account', 'danger')
            print(f"Error: {e}")

    return render_template('portal/portal_signup.html')


@portal_bp.route('/login', methods=['GET', 'POST'])
def portal_login():
    """Login portal for teachers and HODs only"""
    if current_user.is_authenticated:
        if current_user.role == 'teacher':
            return redirect(url_for('teacher.teacher_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')  # Should be either teacher or admin

        user_data = User.get_user_by_email(email)

        if user_data and User.verify_password(user_data['password'], password):
            if user_data['role'] == user_type:
                user = User(user_data)
                login_user(user, remember=True)

                # Redirect based on role
                if user.role == 'teacher':
                    return redirect(url_for('teacher.teacher_dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid user type for this account', 'danger')
        else:
            flash('Login failed. Check your credentials.', 'danger')

    return render_template('portal/portal_login.html')


@portal_bp.route('/logout')
@login_required
def portal_logout():
    logout_user()
    flash('You have been logged out from the portal.', 'info')
    return redirect(url_for('portal.portal_home'))