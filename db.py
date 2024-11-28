from app import db, Student, Quiz


db.create_all()


student = Student(first_name="John", last_name="Smith")
quiz = Quiz(subject="Python Basics", num_questions=5, quiz_date="February 5, 2015")

db.session.add(student)
db.session.add(quiz)
db.session.commit()
