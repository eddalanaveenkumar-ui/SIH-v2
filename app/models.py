from flask_login import UserMixin
from datetime import datetime
import bcrypt
from app import mongo, login_manager
from bson import ObjectId


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.role = user_data['role']
        self.name = user_data.get('name', '')
        self.photo_count = user_data.get('photo_count', 0)
        self._is_active = user_data.get('is_active', True)

    @property
    def is_active(self):
        return self._is_active

    @staticmethod
    def create_user(email, password, role, name=""):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'name': name,
            'created_at': datetime.utcnow(),
            'photo_count': 0,
            'is_active': True
        }
        result = mongo.db.users.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def get_user_by_email(email):
        try:
            return mongo.db.users.find_one({'email': email})
        except:
            return None

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return mongo.db.users.find_one({'_id': ObjectId(user_id)})
        except:
            return None

    @staticmethod
    def verify_password(stored_password, provided_password):
        try:
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
            return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
        except:
            return False


class Attendance:
    @staticmethod
    def mark_attendance(student_email, date, status="present"):
        try:
            # Check if attendance already exists for this student on this date
            existing = mongo.db.attendance.find_one({
                'student_email': student_email,
                'date': date
            })

            if existing:
                # Update existing record
                mongo.db.attendance.update_one(
                    {'_id': existing['_id']},
                    {'$set': {'status': status, 'marked_at': datetime.utcnow()}}
                )
                return existing['_id']
            else:
                # Create new record
                attendance_data = {
                    'student_email': student_email,
                    'date': date,
                    'status': status,
                    'marked_at': datetime.utcnow()
                }
                result = mongo.db.attendance.insert_one(attendance_data)
                return result.inserted_id
        except Exception as e:
            print(f"Error marking attendance: {e}")
            return None

    @staticmethod
    def get_student_attendance(student_email):
        try:
            return list(mongo.db.attendance.find({'student_email': student_email}).sort('date', -1))
        except:
            return []

    @staticmethod
    def get_all_attendance():
        try:
            return list(mongo.db.attendance.find().sort('date', -1))
        except:
            return []

    @staticmethod
    def get_attendance_by_date(date):
        try:
            return list(mongo.db.attendance.find({'date': date}))
        except:
            return []

    @staticmethod
    def get_attendance_by_student_date(student_email, date):
        try:
            return mongo.db.attendance.find_one({
                'student_email': student_email,
                'date': date
            })
        except:
            return None


@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None
    except:
        return None