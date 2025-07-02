from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import os
import secrets
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Secure secret key

# Database initialization
def init_db():
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    # Users table (students and admins)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            gpa REAL DEFAULT 0.0,
            test_score INTEGER DEFAULT 0,
            entry_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Predictions history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            gpa REAL NOT NULL,
            test_score INTEGER NOT NULL,
            prediction_result INTEGER,
            probability REAL,
            confidence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create default admin account
    admin_password = generate_password_hash('admin123')
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, first_name, last_name, role)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin@admissionpredictor.com', admin_password, 'System', 'Administrator', 'admin'))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Machine Learning Model
class AdmissionPredictor:
    def __init__(self):
        # Use Logistic Regression for admission prediction
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.train_model()
    
    def train_model(self):
        """Train the logistic regression model with synthetic data"""
        np.random.seed(42)
        n_samples = 2000  # Increased sample size for better training
        
        # Generate more realistic synthetic data
        gpa = np.random.normal(3.2, 0.6, n_samples)
        gpa = np.clip(gpa, 2.0, 4.0)  # Clip to valid GPA range
        
        test_scores = np.random.normal(1200, 200, n_samples)
        test_scores = np.clip(test_scores, 400, 1600)  # Clip to valid test score range
        
        # Stack features
        X = np.column_stack((gpa, test_scores))
        
        # More realistic admission probability calculation
        # Weighted combination with some randomness
        gpa_weight = 0.45
        test_weight = 0.55
        
        normalized_gpa = (gpa - 2.0) / 2.0  # Normalize GPA to 0-1
        normalized_test = (test_scores - 400) / 1200  # Normalize test scores to 0-1
        
        admission_prob = (normalized_gpa * gpa_weight + normalized_test * test_weight)
        
        # Add some realistic noise and curve
        admission_prob += np.random.normal(0, 0.15, n_samples)
        admission_prob = np.clip(admission_prob, 0, 1)
        
        # Apply sigmoid-like curve to make admission more selective
        admission_prob = 1 / (1 + np.exp(-5 * (admission_prob - 0.6)))
        
        # Convert probabilities to binary outcomes
        y = (admission_prob > 0.5).astype(int)
        
        # Scale features for logistic regression
        X_scaled = self.scaler.fit_transform(X)
        
        # Train the logistic regression model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        print(f"Model trained with {n_samples} samples")
        print(f"Admission rate: {y.mean():.2%}")
        print(f"Model accuracy: {self.model.score(X_scaled, y):.3f}")
    
    def predict_admission(self, gpa, test_score):
        """Make admission prediction using trained logistic regression model"""
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        try:
            # Prepare features and scale them
            features = np.array([[gpa, test_score]])
            features_scaled = self.scaler.transform(features)
            
            # Get prediction probability and class
            probability = self.model.predict_proba(features_scaled)[0][1]
            prediction = self.model.predict(features_scaled)[0]
            
            # Enhanced confidence and messaging system
            if probability >= 0.85:
                confidence = "Very High"
                message = "🎉 Outstanding! You have an excellent chance of admission!"
            elif probability >= 0.70:
                confidence = "High" 
                message = "✨ Great profile! You have a strong chance of admission!"
            elif probability >= 0.50:
                confidence = "Moderate"
                message = "📈 Good foundation! Consider strengthening your profile for better chances!"
            elif probability >= 0.30:
                confidence = "Low"
                message = "📚 Work needed! Focus on improving GPA and test scores!"
            else:
                confidence = "Very Low"
                message = "💪 Significant improvement required. Consider retaking tests and boosting GPA!"
            
            # Add personalized recommendations
            recommendations = []
            if gpa < 3.5:
                recommendations.append("Focus on improving your GPA through consistent study habits")
            if test_score < 1200:
                recommendations.append("Consider test preparation to boost your standardized test scores")
            if gpa >= 3.5 and test_score >= 1200:
                recommendations.append("Excellent academics! Consider strengthening extracurricular activities")
            
            return {
                'prediction': int(prediction),
                'probability': round(probability * 100, 1),
                'confidence': confidence,
                'message': message,
                'recommendations': recommendations,
                'model_type': 'Logistic Regression'
            }
            
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}

predictor = AdmissionPredictor()

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('student_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def get_user_by_id(user_id):
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_prediction(user_id, gpa, test_score, result):
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO predictions (user_id, gpa, test_score, prediction_result, probability, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, gpa, test_score, result.get('prediction', 0), result.get('probability', 0), result.get('confidence', 'Unknown')))
        conn.commit()
    except Exception as e:
        print(f"Error saving prediction: {e}")
    finally:
        conn.close()

# Routes
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('admission_predictor.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[6]
            session['first_name'] = user[4]
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.now(), user[0]))
            conn.commit()
            
            if user[6] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'error')
        
        conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        
        conn = sqlite3.connect('admission_predictor.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            flash('Username or email already exists', 'error')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, first_name, last_name))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # Auto login
        session['user_id'] = user_id
        session['username'] = username
        session['role'] = 'student'
        session['first_name'] = first_name
        
        flash('Registration successful! Welcome!', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('landing'))

@app.route('/dashboard')
@login_required
def student_dashboard():
    user = get_user_by_id(session['user_id'])
    
    # Get recent predictions
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions WHERE user_id = ? 
        ORDER BY created_at DESC LIMIT 5
    ''', (session['user_id'],))
    recent_predictions = cursor.fetchall()
    conn.close()
    
    return render_template('student_dashboard.html', user=user, predictions=recent_predictions)

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "student"')
    total_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM predictions')
    total_predictions = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(gpa) FROM users WHERE role = "student" AND gpa > 0')
    avg_gpa = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        SELECT u.id, u.username, u.first_name, u.last_name, u.email, u.gpa, 
               u.test_score, u.entry_score, u.created_at, u.last_login
        FROM users u WHERE role = 'student' ORDER BY u.created_at DESC
    ''')
    students = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'total_students': total_students,
        'total_predictions': total_predictions,
        'avg_gpa': round(avg_gpa, 2) if avg_gpa else 0
    }
    
    return render_template('admin_dashboard.html', stats=stats, students=students)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.get_json()
        print(f"Received prediction request: {data}")  # Debug logging
        
        # Validate input data exists
        if not data:
            return jsonify({'error': 'Please provide your academic information to get a prediction.'}), 400
        
        # Check for missing or invalid GPA
        if data.get('gpa') is None or data.get('gpa') == '':
            return jsonify({'error': 'Please enter your GPA (Grade Point Average) to continue.'}), 400
        
        # Check for missing or invalid test score
        if data.get('testScore') is None or data.get('testScore') == '':
            return jsonify({'error': 'Please enter your test score (SAT/ACT) to continue.'}), 400
        
        try:
            gpa = float(data['gpa'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Please enter a valid GPA number between 0.0 and 4.0.'}), 400
        
        try:
            test_score = float(data['testScore'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Please enter a valid test score between 200 and 1600.'}), 400
        
        print(f"Parsed values - GPA: {gpa}, Test Score: {test_score}")  # Debug logging
        
        # Validate GPA range
        if not (0.0 <= gpa <= 4.0):
            return jsonify({'error': 'Your GPA must be between 0.0 and 4.0. Please check and enter a valid GPA.'}), 400
        
        # Validate test score range
        if not (200 <= test_score <= 1600):
            return jsonify({'error': 'Test scores must be between 200 and 1600 points. Please enter a valid score.'}), 400
        
        result = predictor.predict_admission(gpa, test_score)
        print(f"Prediction result: {result}")  # Debug logging
        
        if 'error' in result:
            return jsonify({'error': 'Unable to calculate prediction at this time. Please try again.'}), 500
        
        # Save prediction to database
        save_prediction(session['user_id'], gpa, test_score, result)
        
        # Update user's latest scores
        conn = sqlite3.connect('admission_predictor.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET gpa = ?, test_score = ? WHERE id = ?', 
                      (gpa, test_score, session['user_id']))
        conn.commit()
        conn.close()
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Prediction error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Something went wrong while processing your request. Please try again.'}), 500

@app.route('/admin/student/<int:student_id>', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            
            # Handle numeric fields with proper validation
            gpa_str = request.form.get('gpa', '').strip()
            test_score_str = request.form.get('test_score', '').strip()
            entry_score_str = request.form.get('entry_score', '').strip()
            
            # Convert to numbers, handle empty values
            gpa = float(gpa_str) if gpa_str else 0.0
            test_score = int(test_score_str) if test_score_str else 0
            entry_score = float(entry_score_str) if entry_score_str else 0.0
            
            # Validate ranges
            if gpa < 0 or gpa > 4:
                flash('GPA must be between 0.0 and 4.0', 'error')
                return redirect(url_for('edit_student', student_id=student_id))
            
            if test_score < 0 or test_score > 1600:
                flash('Test score must be between 0 and 1600', 'error')
                return redirect(url_for('edit_student', student_id=student_id))
            
            cursor.execute('''
                UPDATE users SET first_name = ?, last_name = ?, email = ?, 
                               gpa = ?, test_score = ?, entry_score = ?
                WHERE id = ? AND role = 'student'
            ''', (first_name, last_name, email, gpa, test_score, entry_score, student_id))
            
            conn.commit()
            flash('Student updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except ValueError as e:
            flash('Invalid input. Please check all fields and try again.', 'error')
            return redirect(url_for('edit_student', student_id=student_id))
        except Exception as e:
            flash('Error updating student. Please try again.', 'error')
            return redirect(url_for('edit_student', student_id=student_id))
    
    cursor.execute('SELECT * FROM users WHERE id = ? AND role = "student"', (student_id,))
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_student.html', student=student)

@app.route('/admin/student/<int:student_id>/delete', methods=['POST'])
@admin_required
def delete_student(student_id):
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    # Delete student's predictions first
    cursor.execute('DELETE FROM predictions WHERE user_id = ?', (student_id,))
    # Delete student
    cursor.execute('DELETE FROM users WHERE id = ? AND role = "student"', (student_id,))
    
    conn.commit()
    conn.close()
    
    flash('Student deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/analytics')
@login_required
def analytics():
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Get user's predictions
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    predictions = cursor.fetchall()
    conn.close()
    
    return render_template('analytics.html', user=user, predictions=predictions)

@app.route('/history')
@login_required
def history():
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Get user's predictions
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    predictions = cursor.fetchall()
    conn.close()
    
    return render_template('history.html', user=user, predictions=predictions)

@app.route('/profile')
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('settings.html', user=user)

@app.route('/settings')
@login_required
def settings():
    user = get_user_by_id(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    return render_template('settings.html', user=user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    username = request.form.get('username')
    
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, email = ?, username = ?
            WHERE id = ?
        ''', (first_name, last_name, email, username, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('settings') + '?success=1')
    except:
        conn.close()
        return redirect(url_for('settings') + '?error=1')

@app.route('/update_academic', methods=['POST'])
@login_required
def update_academic():
    gpa = request.form.get('gpa')
    test_score = request.form.get('test_score')
    
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE users 
            SET gpa = ?, test_score = ?
            WHERE id = ?
        ''', (float(gpa) if gpa else None, int(test_score) if test_score else None, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('settings') + '?success=1')
    except:
        conn.close()
        return redirect(url_for('settings') + '?error=1')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        return redirect(url_for('settings') + '?error=1')
    
    user = get_user_by_id(session['user_id'])
    if not user or not check_password_hash(user[3], current_password):
        return redirect(url_for('settings') + '?error=1')
    
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    try:
        hashed_password = generate_password_hash(new_password)
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE id = ?
        ''', (hashed_password, session['user_id']))
        conn.commit()
        conn.close()
        return redirect(url_for('settings') + '?success=1')
    except:
        conn.close()
        return redirect(url_for('settings') + '?error=1')

@app.route('/clear_history', methods=['POST'])
@login_required
def clear_history():
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM predictions WHERE user_id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except:
        conn.close()
        return jsonify({'success': False})

@app.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'GET':
        return redirect(url_for('settings'))
    
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    try:
        # Delete predictions first (foreign key constraint)
        cursor.execute('DELETE FROM predictions WHERE user_id = ?', (session['user_id'],))
        # Delete user
        cursor.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
        conn.commit()
        conn.close()
        session.clear()
        return redirect(url_for('landing'))
    except:
        conn.close()
        return redirect(url_for('settings') + '?error=1')

# Admin-specific routes
@app.route('/admin/students')
@admin_required
def admin_students():
    # Same as admin dashboard but focus on student management
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    # Get comprehensive analytics
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "student"')
    total_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM predictions')
    total_predictions = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(probability) FROM predictions')
    avg_probability = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        SELECT COUNT(*) as count, confidence 
        FROM predictions 
        GROUP BY confidence 
        ORDER BY count DESC
    ''')
    confidence_stats = cursor.fetchall()
    
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM predictions 
        GROUP BY DATE(created_at) 
        ORDER BY date DESC 
        LIMIT 30
    ''')
    daily_predictions = cursor.fetchall()
    
    conn.close()
    
    analytics_data = {
        'total_students': total_students,
        'total_predictions': total_predictions,
        'avg_probability': round(avg_probability, 1) if avg_probability else 0,
        'confidence_stats': confidence_stats,
        'daily_predictions': daily_predictions
    }
    
    return render_template('admin_analytics.html', data=analytics_data)

@app.route('/admin/predictions')
@admin_required
def admin_predictions():
    conn = sqlite3.connect('admission_predictor.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, u.username, u.first_name, u.last_name 
        FROM predictions p 
        JOIN users u ON p.user_id = u.id 
        ORDER BY p.created_at DESC
    ''')
    all_predictions = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_predictions.html', predictions=all_predictions)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin_settings.html')

@app.route('/admin/export')
@admin_required
def admin_export():
    flash('Export functionality coming soon!', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000) 