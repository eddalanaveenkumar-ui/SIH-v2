from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import mongo
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from bson import ObjectId

auth_bp = Blueprint('auth', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect based on role
        if current_user.role == 'student':
            # Get fresh user data from database
            user_data = User.get_user_by_email(current_user.email)
            if user_data:
                current_user.photo_count = user_data.get('photo_count', 0)

            if current_user.photo_count < 6:
                return redirect(url_for('auth.upload_photos'))
            else:
                return redirect(url_for('student.dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher.teacher_dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        user_data = User.get_user_by_email(email)

        if user_data and User.verify_password(user_data['password'], password):
            if user_data['role'] == user_type:
                user = User(user_data)
                login_user(user, remember=True)

                # Redirect based on role
                if user.role == 'student':
                    # Get fresh photo count from database
                    fresh_user_data = User.get_user_by_email(user.email)
                    if fresh_user_data:
                        user.photo_count = fresh_user_data.get('photo_count', 0)

                    if user.photo_count < 6:
                        return redirect(url_for('auth.upload_photos'))
                    else:
                        return redirect(url_for('student.dashboard'))
                elif user.role == 'teacher':
                    return redirect(url_for('teacher.teacher_dashboard'))
                elif user.role == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Invalid user type for this account', 'danger')
        else:
            flash('Login failed. Check your credentials.', 'danger')

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
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
            return render_template('signup.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('signup.html')

        # Check if user already exists
        if User.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('signup.html')

        # Validate secret codes for teacher and admin
        if user_type == 'teacher':
            if secret_code != "TEACHER123":
                flash('Invalid teacher secret code', 'danger')
                return render_template('signup.html')

        if user_type == 'admin':
            if secret_code != "ADMIN123":
                flash('Invalid admin secret code', 'danger')
                return render_template('signup.html')

        # Create user
        try:
            user_id = User.create_user(email, password, user_type, name)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Error creating user account', 'danger')
            print(f"Error: {e}")

    return render_template('signup.html')


@auth_bp.route('/upload_photos', methods=['GET', 'POST'])
@login_required
def upload_photos():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))

    # Get updated user data
    user_data = User.get_user_by_email(current_user.email)
    if user_data:
        current_user.photo_count = user_data.get('photo_count', 0)

    if request.method == 'POST':
        photos = request.files.getlist('photos')
        uploaded_count = 0

        # Ensure upload directory exists
        os.makedirs('uploads/student_photos', exist_ok=True)

        for photo in photos:
            if photo and photo.filename and allowed_file(photo.filename):
                try:
                    filename = secure_filename(f"{current_user.email}_{datetime.now().timestamp()}_{photo.filename}")
                    photo_path = os.path.join('uploads/student_photos', filename)
                    photo.save(photo_path)
                    uploaded_count += 1
                    print(f"Uploaded: {filename}")
                except Exception as e:
                    print(f"Error uploading file: {e}")
                    flash(f'Error uploading {photo.filename}', 'warning')

        if uploaded_count > 0:
            try:
                # Update photo count in database
                result = mongo.db.users.update_one(
                    {'_id': ObjectId(current_user.id)},
                    {'$inc': {'photo_count': uploaded_count}}
                )

                if result.modified_count > 0:
                    # Update current user object
                    current_user.photo_count += uploaded_count
                    flash(f'Successfully uploaded {uploaded_count} photos! Total: {current_user.photo_count}/6',
                          'success')
                else:
                    flash('Error updating photo count in database', 'danger')

            except Exception as e:
                print(f"Database error: {e}")
                flash('Error updating your profile', 'danger')
        else:
            flash('No valid photos uploaded. Please select image files (PNG, JPG, JPEG, GIF).', 'warning')

        # Check if user has uploaded enough photos
        if current_user.photo_count >= 6:
            return redirect(url_for('student.dashboard'))
        else:
            return redirect(url_for('auth.upload_photos'))

    remaining = max(0, 6 - current_user.photo_count)
    return render_template('student/upload_photos.html',
                           remaining=remaining,
                           current_count=current_user.photo_count)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))