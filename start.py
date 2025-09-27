import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    if not os.path.exists('uploads/student_photos'):
        os.makedirs('uploads/student_photos')

    print("Starting Attendance System...")
    print("Access the application at: http://localhost:5000")
    print("Teacher Secret Code: TEACHER123")
    print("Admin Secret Code: ADMIN123")

    app.run(debug=True, host='0.0.0.0', port=5000)