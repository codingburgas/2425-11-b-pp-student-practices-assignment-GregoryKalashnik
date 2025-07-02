from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, login_user, logout_user
from app.models import Student, Grade, User, Attendance, Subject
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, 
                   email=email,
                   first_name=first_name,
                   last_name=last_name,
                   role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get the user ID
        
        if role == 'student':
            class_year = request.form.get('class_year')
            if not class_year:
                flash('Class year is required for students', 'danger')
                return redirect(url_for('auth.register'))
            try:
                class_year = int(class_year)
                if not (1 <= class_year <= 12):
                    flash('Class year must be between 1 and 12', 'danger')
                    return redirect(url_for('auth.register'))
            except ValueError:
                flash('Invalid class year', 'danger')
                return redirect(url_for('auth.register'))
            student = Student(class_year=class_year, user_id=user.id)
            db.session.add(student)
        
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_teacher():
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.student_dashboard'))
    return render_template('landing.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_teacher():
        total_students = Student.query.count()
        today = datetime.utcnow().date()
        attendance_records = Attendance.query.filter_by(date=today).all()
        present_today = len([a for a in attendance_records if a.status == 'present'])
        absent_today = len([a for a in attendance_records if a.status == 'absent'])
        late_today = len([a for a in attendance_records if a.status == 'late'])
        
        # Calculate attendance rates
        total_attendance = present_today + absent_today + late_today
        present_rate = (present_today / total_attendance * 100) if total_attendance > 0 else 0
        absent_rate = (absent_today / total_attendance * 100) if total_attendance > 0 else 0
        late_rate = (late_today / total_attendance * 100) if total_attendance > 0 else 0
        
        # Get recent grades
        recent_grades = Grade.query.order_by(Grade.date_added.desc()).limit(5).all()
        
        # Calculate grade ranges
        all_grades = Grade.query.all()
        grade_ranges = [
            {'label': 'A (90-100%)', 'min': 90, 'max': 100, 'color': 'bg-success', 'count': 0},
            {'label': 'B (80-89%)', 'min': 80, 'max': 89.99, 'color': 'bg-info', 'count': 0},
            {'label': 'C (70-79%)', 'min': 70, 'max': 79.99, 'color': 'bg-primary', 'count': 0},
            {'label': 'D (60-69%)', 'min': 60, 'max': 69.99, 'color': 'bg-warning', 'count': 0},
            {'label': 'F (0-59%)', 'min': 0, 'max': 59.99, 'color': 'bg-danger', 'count': 0}
        ]
        
        for grade in all_grades:
            for range_info in grade_ranges:
                if range_info['min'] <= grade.grade_value <= range_info['max']:
                    range_info['count'] += 1
                    break
        
        # Calculate performance data
        grades = Grade.query.order_by(Grade.date_added.desc()).all()
        performance_data = []
        performance_labels = []
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_grades = [g.grade_value for g in grades if g.date_added.month == month_date.month]
            if month_grades:
                performance_data.insert(0, sum(month_grades) / len(month_grades))
                performance_labels.insert(0, month_date.strftime('%B'))
        
        return render_template('dashboard.html',
                             total_students=total_students,
                             present_today=present_today,
                             absent_today=absent_today,
                             late_today=late_today,
                             present_rate=present_rate,
                             absent_rate=absent_rate,
                             late_rate=late_rate,
                             recent_grades=recent_grades,
                             grade_ranges=grade_ranges,
                             performance_data=performance_data,
                             performance_labels=performance_labels)
    else:
        return redirect(url_for('main.student_dashboard'))

@main.route('/student_dashboard')
@login_required
def student_dashboard():
    if not current_user.is_student():
        return redirect(url_for('main.dashboard'))
    
    student = current_user.student_profile
    recent_grades = Grade.query.filter_by(student_id=student.id).order_by(Grade.date_added.desc()).limit(5).all()
    subjects = Subject.query.all()
    
    # Get attendance for the current month
    today = datetime.utcnow()
    start_date = today.replace(day=1)
    
    # Get last 6 months of attendance
    monthly_data = []
    monthly_labels = []
    
    for i in range(6):
        month_date = (today - timedelta(days=30*i))
        month_start = month_date.replace(day=1)
        if i < 5:
            month_end = (month_start + timedelta(days=32)).replace(day=1)
        else:
            month_end = month_date
            
        month_attendance = Attendance.query.filter_by(student_id=student.id)\
            .filter(Attendance.date >= month_start)\
            .filter(Attendance.date < month_end).all()
            
        total = len(month_attendance)
        if total > 0:
            present = len([a for a in month_attendance if a.status == 'present'])
            rate = round((present / total) * 100)
        else:
            rate = 0
            
        monthly_data.append(rate)
        monthly_labels.append(month_date.strftime('%B'))
    
    # Reverse the lists so they're in chronological order
    monthly_data.reverse()
    monthly_labels.reverse()
    
    # Current month attendance stats
    current_month_attendance = Attendance.query.filter_by(student_id=student.id)\
        .filter(Attendance.date >= start_date).all()
    
    attendance_stats = {
        'present': len([a for a in current_month_attendance if a.status == 'present']),
        'absent': len([a for a in current_month_attendance if a.status == 'absent']),
        'late': len([a for a in current_month_attendance if a.status == 'late'])
    }
    
    return render_template('student_dashboard.html',
                         student=student,
                         recent_grades=recent_grades,
                         subjects=subjects,
                         attendance_stats=attendance_stats,
                         monthly_attendance_data=monthly_data,
                         monthly_attendance_labels=monthly_labels)

@main.route('/students')
@login_required
def students():
    if not current_user.is_teacher():
        return redirect(url_for('main.dashboard'))
    
    students = Student.query.all()
    return render_template('students.html', students=students)

@main.route('/student/<int:student_id>')
@login_required
def student_profile(student_id):
    if not current_user.is_teacher():
        return redirect(url_for('main.dashboard'))
    
    student = Student.query.get_or_404(student_id)
    grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.date_added.desc()).all()
    attendance = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).all()
    subjects = Subject.query.all()
    
    # Calculate statistics
    total_grades = len(grades)
    avg_grade = sum(g.grade_value for g in grades) / total_grades if total_grades > 0 else 0
    
    total_attendance = len(attendance)
    attendance_rate = len([a for a in attendance if a.status == 'present']) / total_attendance * 100 if total_attendance > 0 else 0
    
    return render_template('student_profile.html', 
                         student=student,
                         grades=grades,
                         attendance=attendance,
                         subjects=subjects,
                         avg_grade=avg_grade,
                         attendance_rate=attendance_rate)

@main.route('/grades', methods=['GET', 'POST'])
@login_required
def grades():
    if not current_user.is_teacher():
        flash('Access denied. This page is only for teachers.', 'danger')
        return redirect(url_for('main.student_grades'))

    students = Student.query.all()
    subjects = Subject.query.all()
    grades = Grade.query.order_by(Grade.date_added.desc()).all()
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        grade_value = request.form.get('grade_value')
        grade_type = request.form.get('grade_type')
        comment = request.form.get('comment')

        if not all([student_id, subject_id, grade_value, grade_type]):
            flash('All fields except comment are required', 'danger')
            return redirect(url_for('main.grades'))

        try:
            grade_value = float(grade_value)
            if not (0 <= grade_value <= 100):
                flash('Grade must be between 0 and 100', 'danger')
                return redirect(url_for('main.grades'))
        except ValueError:
            flash('Invalid grade value', 'danger')
            return redirect(url_for('main.grades'))

        grade = Grade(
            student_id=student_id,
            subject_id=subject_id,
            grade_value=grade_value,
            grade_type=grade_type,
            comment=comment,
            date_added=datetime.utcnow(),
            added_by=current_user.id  # Add the current teacher's ID
        )
        
        db.session.add(grade)
        try:
            db.session.commit()
            flash('Grade added successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding grade: {str(e)}', 'danger')
        
        return redirect(url_for('main.grades'))

    # Calculate statistics
    total_grades = len(grades)
    avg_grade = sum(grade.grade_value for grade in grades) / total_grades if total_grades > 0 else 0
    highest_grade = max((grade.grade_value for grade in grades), default=0)
    lowest_grade = min((grade.grade_value for grade in grades), default=0)
    
    return render_template('grades.html',
                         students=students,
                         subjects=subjects,
                         grades=grades,
                         total_grades=total_grades,
                         avg_grade=avg_grade,
                         highest_grade=highest_grade,
                         lowest_grade=lowest_grade)

@main.route('/student_grades')
@login_required
def student_grades():
    if current_user.role != 'student':
        flash('Access denied. This page is only for students.', 'danger')
        return redirect(url_for('main.dashboard'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    subjects = Subject.query.all()
    
    # Get all grades for the student
    grades = Grade.query.filter_by(student_id=student.id).all()
    
    # Calculate overall GPA
    overall_gpa = sum(grade.grade_value for grade in grades) / len(grades) if grades else 0
    
    # Get highest grade
    highest_grade = max((grade.grade_value for grade in grades), default=0)
    
    # Calculate subject averages
    subject_grades = {}
    subject_averages = {}
    for subject in subjects:
        subject_grades[subject.id] = [g for g in grades if g.subject_id == subject.id]
        if subject_grades[subject.id]:
            subject_averages[subject.id] = sum(g.grade_value for g in subject_grades[subject.id]) / len(subject_grades[subject.id])
        else:
            subject_averages[subject.id] = 0
    
    # Calculate grade distribution
    grade_ranges = ['0-59', '60-69', '70-79', '80-89', '90-100']
    grade_distribution = [0] * 5
    for grade in grades:
        if grade.grade_value < 60:
            grade_distribution[0] += 1
        elif grade.grade_value < 70:
            grade_distribution[1] += 1
        elif grade.grade_value < 80:
            grade_distribution[2] += 1
        elif grade.grade_value < 90:
            grade_distribution[3] += 1
        else:
            grade_distribution[4] += 1
    
    return render_template('student/grades.html',
                         student=student,
                         subjects=subjects,
                         overall_gpa=overall_gpa,
                         highest_grade=highest_grade,
                         total_assessments=len(grades),
                         subject_grades=subject_grades,
                         subject_averages=subject_averages,
                         grade_ranges=grade_ranges,
                         grade_distribution=grade_distribution)

@main.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if not current_user.is_teacher():
        flash('Access denied. This page is only for teachers.', 'danger')
        return redirect(url_for('main.student_attendance'))

    students = Student.query.all()
    subjects = Subject.query.all()
    today = datetime.utcnow().date()
    today_attendance = Attendance.query.filter_by(date=today).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject_id = request.form.get('subject_id')
        status = request.form.get('status')
        comment = request.form.get('comment', '')

        if not all([student_id, subject_id, status]):
            flash('Student, subject, and status are required', 'danger')
            return redirect(url_for('main.attendance'))

        # Check if attendance already recorded for this student, subject, and date
        existing_attendance = Attendance.query.filter_by(
            student_id=student_id,
            subject_id=subject_id,
            date=today
        ).first()

        if existing_attendance:
            flash('Attendance already recorded for this student and subject today', 'warning')
            return redirect(url_for('main.attendance'))

        if status not in ['present', 'absent', 'late']:
            flash('Invalid attendance status', 'danger')
            return redirect(url_for('main.attendance'))

        attendance_record = Attendance(
            student_id=student_id,
            subject_id=subject_id,
            date=today,
            status=status,
            comment=comment,
            recorded_by=current_user.id
        )

        db.session.add(attendance_record)
        try:
            db.session.commit()
            flash('Attendance recorded successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording attendance: {str(e)}', 'danger')

        return redirect(url_for('main.attendance'))
    
    return render_template('attendance.html',
                         students=students,
                         subjects=subjects,
                         attendance_records=today_attendance,
                         today=today)

@main.route('/student_attendance')
@login_required
def student_attendance():
    if current_user.role != 'student':
        flash('Access denied. This page is only for students.', 'danger')
        return redirect(url_for('main.dashboard'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Get attendance records
    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    
    # Calculate attendance statistics
    attendance_stats = {
        'present': sum(1 for a in attendance_records if a.status == 'present'),
        'absent': sum(1 for a in attendance_records if a.status == 'absent'),
        'late': sum(1 for a in attendance_records if a.status == 'late')
    }
    
    total_records = len(attendance_records)
    attendance_rate = (attendance_stats['present'] / total_records * 100) if total_records > 0 else 0
    
    # Get monthly data
    monthly_data = {}
    for record in attendance_records:
        month = record.date.strftime('%Y-%m')
        if month not in monthly_data:
            monthly_data[month] = {'present': 0, 'absent': 0, 'late': 0}
        monthly_data[month][record.status] += 1
    
    monthly_labels = list(monthly_data.keys())
    monthly_present = [monthly_data[m]['present'] for m in monthly_labels]
    monthly_absent = [monthly_data[m]['absent'] for m in monthly_labels]
    monthly_late = [monthly_data[m]['late'] for m in monthly_labels]
    
    # Get subject-wise attendance
    subjects = Subject.query.all()
    subject_names = [subject.name for subject in subjects]
    subject_present = []
    subject_absent = []
    subject_late = []
    
    for subject in subjects:
        subject_records = [r for r in attendance_records if r.subject_id == subject.id]
        subject_present.append(sum(1 for r in subject_records if r.status == 'present'))
        subject_absent.append(sum(1 for r in subject_records if r.status == 'absent'))
        subject_late.append(sum(1 for r in subject_records if r.status == 'late'))
    
    return render_template('student/attendance.html',
                         student=student,
                         attendance_records=attendance_records,
                         attendance_stats=attendance_stats,
                         attendance_rate=attendance_rate,
                         monthly_labels=monthly_labels,
                         monthly_present=monthly_present,
                         monthly_absent=monthly_absent,
                         monthly_late=monthly_late,
                         subject_names=subject_names,
                         subject_present=subject_present,
                         subject_absent=subject_absent,
                         subject_late=subject_late,
                         months=sorted(set(r.date.strftime('%B %Y') for r in attendance_records)))

@main.route('/reports')
@login_required
def reports():
    if current_user.is_teacher():
        students = Student.query.all()
        subjects = Subject.query.all()
        grades = Grade.query.order_by(Grade.date_added.desc()).all()
        attendance_records = Attendance.query.order_by(Attendance.date.desc()).all()
        
        # Calculate performance data
        performance_data = []
        performance_labels = []
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_grades = [g.grade_value for g in grades if g.date_added.month == month_date.month]
            if month_grades:
                performance_data.insert(0, sum(month_grades) / len(month_grades))
                performance_labels.insert(0, month_date.strftime('%B'))
        
        return render_template('reports.html',
                             students=students,
                             subjects=subjects,
                             grades=grades,
                             attendance_records=attendance_records,
                             performance_data=performance_data,
                             performance_labels=performance_labels)
    else:
        flash('Access denied. This page is only for teachers.', 'danger')
        return redirect(url_for('main.student_reports'))

@main.route('/student_reports')
@login_required
def student_reports():
    if current_user.role != 'student':
        flash('Access denied. This page is only for students.', 'danger')
        return redirect(url_for('main.dashboard'))

    student = Student.query.filter_by(user_id=current_user.id).first()
    subjects = Subject.query.all()
    
    # Get grades and attendance
    grades = Grade.query.filter_by(student_id=student.id).order_by(Grade.date_added.desc()).all()
    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    
    # Calculate overall GPA
    overall_gpa = sum(grade.grade_value for grade in grades) / len(grades) if grades else 0
    
    # Calculate attendance rate
    total_records = len(attendance_records)
    attendance_stats = {
        'present': sum(1 for a in attendance_records if a.status == 'present'),
        'absent': sum(1 for a in attendance_records if a.status == 'absent'),
        'late': sum(1 for a in attendance_records if a.status == 'late')
    }
    attendance_rate = (attendance_stats['present'] / total_records * 100) if total_records > 0 else 0
    
    # Calculate subject averages and attendance
    subject_averages = {}
    subject_attendance = {}
    for subject in subjects:
        subject_grades = [g for g in grades if g.subject_id == subject.id]
        subject_averages[subject.id] = sum(g.grade_value for g in subject_grades) / len(subject_grades) if subject_grades else 0
        
        subject_records = [r for r in attendance_records if r.subject_id == subject.id]
        if subject_records:
            present_count = sum(1 for r in subject_records if r.status == 'present')
            subject_attendance[subject.id] = (present_count / len(subject_records)) * 100
        else:
            subject_attendance[subject.id] = 0
    
    # Get progress data (last 6 months)
    progress_data = []
    progress_labels = []
    for i in range(6):
        month_date = datetime.now() - timedelta(days=30*i)
        month_grades = [g.grade_value for g in grades if g.date_added.month == month_date.month]
        if month_grades:
            progress_data.insert(0, sum(month_grades) / len(month_grades))
            progress_labels.insert(0, month_date.strftime('%B'))
    
    return render_template('student/reports.html',
                         student=student,
                         subjects=subjects,
                         overall_gpa=overall_gpa,
                         attendance_rate=attendance_rate,
                         attendance_stats=attendance_stats,
                         subject_averages=subject_averages,
                         subject_attendance=subject_attendance,
                         recent_grades=grades[:5],
                         progress_data=progress_data,
                         progress_labels=progress_labels)

@main.route('/download_report/<report_type>')
@login_required
def download_report(report_type):
    if current_user.role != 'student':
        flash('Access denied. This page is only for students.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # This is a placeholder - implement actual PDF generation
    flash(f'Download {report_type} report functionality will be implemented soon.', 'info')
    return redirect(url_for('main.reports'))

@main.route('/profile')
@login_required
def profile():
    # Get relevant data based on user role
    if current_user.is_teacher():
        students = Student.query.all()
        subjects = Subject.query.all()
        activities = []  # We'll implement this later
        return render_template('profile.html',
                             students=students,
                             subjects=subjects,
                             activities=activities)
    else:
        student = Student.query.filter_by(user_id=current_user.id).first()
        subjects = Subject.query.all()
        activities = []  # We'll implement this later
        return render_template('profile.html',
                             student=student,
                             subjects=subjects,
                             activities=activities)

@main.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create a unique filename to avoid conflicts
            unique_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            
            # Update user's profile picture path
            current_user.profile_picture = unique_filename
            db.session.commit()
            flash('Profile picture updated successfully!', 'success')
        else:
            flash('Invalid file type. Please upload an image file.', 'error')
    
    # Handle other profile updates here
    return redirect(url_for('main.profile'))

@main.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@main.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    if request.method == 'POST':
        # Update password if provided
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if current_password and new_password:
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect!', 'danger')
                return redirect(url_for('main.settings'))

        # Update notification preferences
        current_user.email_notifications = 'email_notifications' in request.form
        current_user.sms_notifications = 'sms_notifications' in request.form
        
        # Update theme preference
        current_user.theme = request.form.get('theme', 'light')
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))

@main.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@main.route('/subjects/add', methods=['POST'])
@login_required
def add_subject():
    if not current_user.is_teacher():
        flash('Access denied. Teachers only.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Subject name is required.', 'danger')
        return redirect(url_for('main.subjects'))
    
    subject = Subject(name=name, description=description)
    db.session.add(subject)
    db.session.commit()
    
    flash('Subject added successfully!', 'success')
    return redirect(url_for('main.subjects'))

@main.route('/api/subjects/<int:id>', methods=['DELETE'])
@login_required
def delete_subject(id):
    if not current_user.is_teacher():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({'success': True})

@main.route('/my_grades')
@login_required
def my_grades():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    grades = Grade.query.filter_by(student_id=student.id).all()
    return render_template('my_grades.html', grades=grades)

@main.route('/my_attendance')
@login_required
def my_attendance():
    if not current_user.is_student():
        flash('Access denied. Students only.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    attendance = Attendance.query.filter_by(student_id=student.id).all()
    return render_template('my_attendance.html', attendance=attendance)

# API endpoints for AJAX requests
@main.route('/api/student/<int:student_id>/grades')
@login_required
def student_grades_api(student_id):
    grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.date_added.desc()).all()
    return jsonify([{
        'subject': g.subject.name,
        'value': g.grade_value,
        'type': g.grade_type,
        'date': g.date_added.strftime('%Y-%m-%d'),
        'comment': g.comment
    } for g in grades])

@main.route('/api/student/<int:student_id>/attendance')
@login_required
def student_attendance_api(student_id):
    attendance = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).all()
    return jsonify([{
        'subject': a.subject.name,
        'date': a.date.strftime('%Y-%m-%d'),
        'status': a.status,
        'comment': a.comment
    } for a in attendance])
