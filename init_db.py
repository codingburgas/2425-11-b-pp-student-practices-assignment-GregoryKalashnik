from app import create_app, db
from app.models import User, Student, Subject, Grade, Attendance
from datetime import datetime, date
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()

        # Create a teacher user
        teacher = User(
            username='teacher',
            email='teacher@example.com',
            first_name='John',
            last_name='Smith',
            role='teacher'
        )
        teacher.set_password('password123')
        db.session.add(teacher)
        db.session.commit()

        # Create some subjects
        subjects = [
            Subject(name='Mathematics', description='Mathematics course covering algebra and calculus'),
            Subject(name='Physics', description='Physics course covering mechanics and thermodynamics'),
            Subject(name='Chemistry', description='Chemistry course covering organic and inorganic chemistry')
        ]
        for subject in subjects:
            db.session.add(subject)
        db.session.commit()

        # Create some student users and their profiles
        students_data = [
            ('student1', 'Alice', 'Johnson', 2025),
            ('student2', 'Bob', 'Wilson', 2025),
            ('student3', 'Charlie', 'Brown', 2024)
        ]

        for username, fname, lname, year in students_data:
            # Create user
            student_user = User(
                username=username,
                email=f'{username}@example.com',
                first_name=fname,
                last_name=lname,
                role='student'
            )
            student_user.set_password('password123')
            db.session.add(student_user)
            db.session.commit()

            # Create student profile
            student = Student(
                class_year=year,
                user_id=student_user.id
            )
            db.session.add(student)
            db.session.commit()

            # Add some grades
            for subject in subjects:
                grade = Grade(
                    student_id=student.id,
                    subject_id=subject.id,
                    grade_value=85.0,
                    grade_type='Quiz',
                    comment='Good work',
                    added_by=teacher.id,
                    date_added=datetime.utcnow()
                )
                db.session.add(grade)

            # Add attendance records
            for subject in subjects:
                attendance = Attendance(
                    student_id=student.id,
                    subject_id=subject.id,
                    date=date.today(),
                    status='present',
                    recorded_by=teacher.id
                )
                db.session.add(attendance)

        # Commit all remaining changes
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
