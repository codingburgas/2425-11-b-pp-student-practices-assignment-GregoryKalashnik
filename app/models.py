from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    role = db.Column(db.String(20))  # 'student' or 'teacher'
    profile_picture = db.Column(db.String(255))  # Path to profile picture
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    theme = db.Column(db.String(20), default='light')  # light, dark, or system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_year = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', backref=db.backref('student_profile', uselist=False))
    grades = db.relationship('Grade', backref='student', lazy='dynamic')
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic')

    @property
    def full_name(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return "Unknown"

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    grades = db.relationship('Grade', backref='subject', lazy='dynamic')
    attendance_records = db.relationship('Attendance', backref='subject', lazy='dynamic')

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    grade_value = db.Column(db.Float, nullable=False)
    grade_type = db.Column(db.String(20), nullable=False)  # Quiz, Test, Homework, etc.
    comment = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Late
    comment = db.Column(db.Text)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_by_user = db.relationship('User', backref=db.backref('recorded_attendance', lazy='dynamic'), foreign_keys=[recorded_by])

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
