from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import Attendance
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/mark', methods=['POST'])
@login_required
def mark_attendance():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    student_email = data.get('student_email')
    date = data.get('date', datetime.now().date().isoformat())
    status = data.get('status', 'present')

    # Check if attendance already marked for today
    existing = Attendance.get_attendance_by_student_date(student_email, date)
    if existing:
        return jsonify({'error': 'Attendance already marked for this date'}), 400

    Attendance.mark_attendance(student_email, date, status)
    return jsonify({'success': True, 'message': 'Attendance marked successfully'})


@attendance_bp.route('/student/<student_email>')
@login_required
def get_student_attendance(student_email):
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'Unauthorized'}), 403

    records = Attendance.get_student_attendance(student_email)
    attendance_data = []
    for record in records:
        attendance_data.append({
            'date': record['date'],
            'status': record['status'],
            'marked_at': record['marked_at']
        })

    return jsonify(attendance_data)


@attendance_bp.route('/date/<date>')
@login_required
def get_attendance_by_date(date):
    if current_user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'Unauthorized'}), 403

    records = Attendance.get_attendance_by_date(date)
    attendance_data = []
    for record in records:
        attendance_data.append({
            'student_email': record['student_email'],
            'status': record['status'],
            'marked_at': record['marked_at']
        })

    return jsonify(attendance_data)