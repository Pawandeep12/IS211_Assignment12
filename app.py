from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hw13.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

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

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid username or password!', 'error')
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    students = Student.query.all()
    quizzes = Quiz.query.all()
    return render_template('dashboard.html', students=students, quizzes=quizzes)

# Add Student
@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        if first_name and last_name:
            new_student = Student(first_name=first_name, last_name=last_name)
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash('All fields are required!', 'error')
    return render_template('add_student.html')

# Add Quiz
@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        if subject and num_questions and quiz_date:
            new_quiz = Quiz(
                subject=subject,
                num_questions=int(num_questions),
                quiz_date=datetime.strptime(quiz_date, '%Y-%m-%d')
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash('All fields are required!', 'error')
    return render_template('add_quiz.html')

# View Results
@app.route('/student/<int:id>')
def view_results(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    student = Student.query.get_or_404(id)
    results = db.session.query(Result, Quiz).join(Quiz).filter(Result.student_id == id).all()
    return render_template('view_results.html', student=student, results=results)

# Add Quiz Result
@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    students = Student.query.all()
    quizzes = Quiz.query.all()

    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        if student_id and quiz_id and score:
            new_result = Result(student_id=int(student_id), quiz_id=int(quiz_id), score=int(score))
            db.session.add(new_result)
            db.session.commit()
            flash('Quiz result added successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash('All fields are required!', 'error')
    return render_template('add_result.html', students=students, quizzes=quizzes)

if __name__ == '__main__':
    with app.app_context():  
        db.create_all()      
    app.run(debug=True)

