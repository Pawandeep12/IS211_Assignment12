from flask import Flask, render_template, request, redirect, url_for, flash
from app import db, Student


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
