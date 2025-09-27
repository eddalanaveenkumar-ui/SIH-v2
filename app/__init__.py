from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from config import Config

mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    login_manager.init_app(app)

    # Import blueprints
    from app.routes import main_routes, student_routes, teacher_routes, admin_routes
    from app.auth import auth_bp
    from app.attendance import attendance_bp
    from app.portal_routes import portal_bp

    # Register blueprints with unique names
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(student_routes, url_prefix='/student')
    app.register_blueprint(teacher_routes, url_prefix='/teacher')
    app.register_blueprint(admin_routes, url_prefix='/admin')
    app.register_blueprint(portal_bp, url_prefix='/portal')  # Add prefix

    return app