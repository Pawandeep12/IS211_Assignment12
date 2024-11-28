from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hw13.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Hardcoded login credentials
USERNAME = 'admin'
PASSWORD = 'password'

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)
    quiz_date = db.Column(db.String(50), nullable=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard route to display students and quizzes."""
    if not session.get('logged_in'):
        flash('You must log in first.', 'error')
        return redirect(url_for('login'))
    
    students = Student.query.all()  # Fetch all students
    quizzes = Quiz.query.all()      # Fetch all quizzes
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/logout')
def logout():
    """Log out the user."""
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
# Add Student Page
@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if not first_name or not last_name:
            # Return error if form is incomplete
            flash("Both first name and last name are required.", "error")
            return render_template('add_student.html')

        # Create a new Student object
        new_student = Student(first_name=first_name, last_name=last_name)

        try:
            # Add to database
            db.session.add(new_student)
            db.session.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding student: {str(e)}", "error")
            return render_template('add_student.html')

    return render_template('add_student.html')

