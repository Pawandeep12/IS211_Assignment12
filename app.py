from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hw13.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

# Routes
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Please try again.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    students = Student.query.all()
    quizzes = Quiz.query.all()
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        if not first_name or not last_name:
            flash('Please fill out all fields.')
            return render_template('add_student.html')
        new_student = Student(first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        subject = request.form.get('subject')
        num_questions = request.form.get('num_questions')
        quiz_date = request.form.get('quiz_date')
        if not subject or not num_questions or not quiz_date:
            flash('Please fill out all fields.')
            return render_template('add_quiz.html')
        new_quiz = Quiz(subject=subject, num_questions=int(num_questions), quiz_date=datetime.strptime(quiz_date, '%Y-%m-%d'))
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz added successfully!')
        return redirect(url_for('dashboard'))
    return render_template('add_quiz.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
