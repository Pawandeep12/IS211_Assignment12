from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hw13.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


USERNAME = 'admin'
PASSWORD = 'password'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    num_questions = db.Column(db.Integer, nullable=False)
    quiz_date = db.Column(db.String(50), nullable=False)

class StudentResult(db.Model):
    __tablename__ = 'student_results'

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))

    
    student = db.relationship('Student', backref='results')
    quiz = db.relationship('Quiz', backref='results')

    def __repr__(self):
        return f'<StudentResult {self.student.first_name} {self.student.last_name} - {self.quiz.subject}>'


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
    
    students = Student.query.all()  
    quizzes = Quiz.query.all()      
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/logout')
def logout():
    """Log out the user."""
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
      
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if not first_name or not last_name:
          
            flash("Both first name and last name are required.", "error")
            return render_template('add_student.html')

        
        new_student = Student(first_name=first_name, last_name=last_name)

        try:
          
            db.session.add(new_student)
            db.session.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding student: {str(e)}", "error")
            return render_template('add_student.html')

    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        
        subject = request.form.get('subject')
        num_questions = request.form.get('num_questions')
        quiz_date = request.form.get('quiz_date')

        if not subject or not num_questions or not quiz_date:
            
            flash("All fields are required.", "error")
            return render_template('add_quiz.html')

        try:
            
            quiz_date_parsed = datetime.strptime(quiz_date, '%Y-%m-%d')

         
            new_quiz = Quiz(subject=subject, num_questions=int(num_questions), quiz_date=quiz_date_parsed)

            
            db.session.add(new_quiz)
            db.session.commit()
            flash("Quiz added successfully!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding quiz: {str(e)}", "error")
            return render_template('add_quiz.html')

    return render_template('add_quiz.html')

@app.route('/student/<int:student_id>', methods=['GET'])
def view_student_results(student_id):
    
    student = Student.query.get(student_id)

    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('dashboard'))

    
    results = db.session.query(Quiz, StudentResult).join(StudentResult).filter(StudentResult.student_id == student.id).all()

   
    if not results:
        return render_template('student_results.html', student=student, results=None)

    
    return render_template('student_results.html', student=student, results=results)

@app.route('/results/add', methods=['GET', 'POST'])
def add_quiz_result():
   
    students = Student.query.all()
    quizzes = Quiz.query.all()

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        quiz_id = request.form.get('quiz_id')
        score = request.form.get('score')

       
        if not student_id or not quiz_id or not score:
            flash('All fields are required!', 'error')
            return render_template('add_quiz_result.html', students=students, quizzes=quizzes)

        
        try:
            score = int(score)
            if not (0 <= score <= 100):
                raise ValueError("Score must be between 0 and 100.")
        except ValueError:
            flash('Score must be a valid number between 0 and 100.', 'error')
            return render_template('add_quiz_result.html', students=students, quizzes=quizzes)

      
        quiz_result = StudentResult(student_id=student_id, quiz_id=quiz_id, score=score)
        db.session.add(quiz_result)
        db.session.commit()

        flash('Quiz result added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_quiz_result.html', students=students, quizzes=quizzes)

