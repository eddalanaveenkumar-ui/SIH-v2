import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/attendance_system'
    UPLOAD_FOLDER = 'uploads/student_photos'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Secret codes for teacher and admin registration
    TEACHER_SECRET_CODE = "TEACHER123"
    ADMIN_SECRET_CODE = "ADMIN123"