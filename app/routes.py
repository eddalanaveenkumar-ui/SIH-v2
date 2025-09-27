from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user, logout_user
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename
from app.models import User, Attendance
from app import mongo
from bson import ObjectId

main_routes = Blueprint('main', __name__)
student_routes = Blueprint('student', __name__)
teacher_routes = Blueprint('teacher', __name__)
admin_routes = Blueprint('admin', __name__)


@main_routes.route('/')
def index():
    return render_template('index.html')


# Student Dashboard - SIMPLIFIED VERSION
@student_routes.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return redirect(url_for('main.index'))

    try:
        # Get fresh user data from database
        user_data = User.get_user_by_email(current_user.email)
        if not user_data:
            flash('User data not found. Please login again.', 'danger')
            return redirect(url_for('auth.logout'))

        # Update current user's photo count
        current_user.photo_count = user_data.get('photo_count', 0)
        current_user.name = user_data.get('name', 'User')

        # Check if student has uploaded enough photos
        if current_user.photo_count < 6:
            flash(f'Please upload {6 - current_user.photo_count} more photos to access full dashboard', 'warning')
            # Still show dashboard but with warning

        # Get attendance records - handle empty case
        try:
            attendance_records = Attendance.get_student_attendance(current_user.email)
            if attendance_records is None:
                attendance_records = []
        except Exception as e:
            print(f"Error getting attendance: {e}")
            attendance_records = []

        # Calculate attendance summary safely
        total_days = len(attendance_records)
        present_days = 0

        for record in attendance_records:
            if isinstance(record, dict) and record.get('status') == 'present':
                present_days += 1

        return render_template('student/dashboard.html',
                               attendance_records=attendance_records,
                               total_days=total_days,
                               present_days=present_days)

    except Exception as e:
        flash('Error loading dashboard. Please try again.', 'danger')
        print(f"Dashboard error: {str(e)}")
        # Instead of redirecting to index, show a simple error page
        return render_template('student/dashboard.html',
                               attendance_records=[],
                               total_days=0,
                               present_days=0)


# Teacher Dashboard
@teacher_routes.route('/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        return redirect(url_for('main.index'))

    # Get all students
    try:
        students = list(mongo.db.users.find({'role': 'student', 'is_active': True}))
    except:
        students = []

    # Get today's attendance
    today = date.today().isoformat()
    try:
        today_attendance = Attendance.get_attendance_by_date(today)
        present_today = len([record for record in today_attendance if record.get('status') == 'present'])
        absent_today = len([record for record in today_attendance if record.get('status') == 'absent'])
    except:
        today_attendance = []
        present_today = 0
        absent_today = 0

    return render_template('teacher/dashboard.html',
                           total_students=len(students),
                           present_today=present_today,
                           absent_today=absent_today,
                           today=today)


@teacher_routes.route('/attendance')
@login_required
def attendance_view():
    if current_user.role != 'teacher':
        return redirect(url_for('main.index'))

    date_filter = request.args.get('date', date.today().isoformat())
    try:
        attendance_records = Attendance.get_attendance_by_date(date_filter)
        # Get student details for each record
        for record in attendance_records:
            student = User.get_user_by_email(record['student_email'])
            record['student_name'] = student['name'] if student else 'Unknown'
    except:
        attendance_records = []

    return render_template('teacher/attendance_view.html',
                           attendance_records=attendance_records,
                           selected_date=date_filter)


# Admin Dashboard
@admin_routes.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))

    try:
        total_students = mongo.db.users.count_documents({'role': 'student', 'is_active': True})
        total_teachers = mongo.db.users.count_documents({'role': 'teacher', 'is_active': True})
        total_attendance = mongo.db.attendance.count_documents({})
    except:
        total_students = 0
        total_teachers = 0
        total_attendance = 0

    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_attendance=total_attendance)


@admin_routes.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))

    try:
        users = list(mongo.db.users.find())
    except:
        users = []

    return render_template('admin/manage_users.html', users=users)


@admin_routes.route('/manage_attendance')
@login_required
def manage_attendance():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))

    try:
        attendance_records = Attendance.get_all_attendance()
    except:
        attendance_records = []

    return render_template('admin/manage_attendance.html', attendance_records=attendance_records)