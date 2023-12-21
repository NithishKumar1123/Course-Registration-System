from flask import Flask
from flask import render_template
from flask import request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)
    courses = db.relationship("Course", secondary = "enrollments")

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable = False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable = False)

@app.route('/')
def student_index():
    students = Student.query.all()
    return render_template('student_index.html', students = students)

@app.route('/student/create', methods = ["GET", "POST"])
def student_create():
    if request.method == "GET":
        return render_template("student_create.html")
    else:
        roll = request.form["roll"]
        f_name = request.form["f_name"]
        l_name = request.form["l_name"]
        data = Student.query.filter_by(roll_number = roll).all()
        if(data == []):
            new_student = Student(roll_number = roll, first_name = f_name, last_name = l_name)
            db.session.add(new_student)
            db.session.commit()
            return redirect("/")
        else:
            return render_template("student_exist.html")

@app.route("/student/<int:student_id>/update", methods = ["GET", "POST"])
def student_update(student_id):
    if request.method == "GET":
        student = Student.query.filter_by(student_id = student_id).first()
        course = Course.query.all()
        return render_template("student_update.html", student = student, courses = course)
    else:
        f_name = request.form["f_name"]
        l_name = request.form["l_name"]
        try:
            course_id = request.form["courses"]
            course = Course.query.filter_by(course_id = course_id).first()
            enroll = Enrollments.query.filter_by(estudent_id = student_id, ecourse_id = course_id).first()
            if(enroll == None):
                new_enrollment = Enrollments(estudent_id = student_id, ecourse_id = course_id)
                db.session.add(new_enrollment)
        except:
           pass 
        student = Student.query.filter_by(student_id = student_id).first()
        student.first_name = f_name
        student.last_name = l_name
        db.session.commit()
        return redirect("/")

@app.route("/student/<int:student_id>/delete")
def student_delete(student_id):
    enroll = Enrollments.query.filter_by(estudent_id = student_id).all()
    for row in enroll:
        db.session.delete(row)
    student = Student.query.filter_by(student_id = student_id).first()
    db.session.delete(student)
    db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>")
def student_display(student_id):
    students = Student.query.filter_by(student_id = student_id).all()
    enroll = Enrollments.query.filter_by(estudent_id = student_id).all()
    courses = []
    for row in enroll:
        courses.append(Course.query.filter_by(course_id = row.ecourse_id).one())
    return render_template("student_display.html", students = students, courses = courses)

@app.route("/student/<int:student_id>/withdraw/<int:course_id>")
def withdraw(student_id, course_id):
    enroll = Enrollments.query.filter_by(estudent_id = student_id, ecourse_id = course_id).all()
    for row in enroll:
        db.session.delete(row)
    db.session.commit()
    return redirect("/")

@app.route("/courses")
def course_index():
    courses = Course.query.all()
    return render_template("course_index.html", courses = courses)

@app.route("/course/create", methods = ["GET", "POST"])
def course_create():
    if request.method == "GET":
        return render_template("course_create.html")
    else:
        code = request.form["code"]
        c_name = request.form["c_name"]
        desc = request.form["desc"]
        data = Course.query.filter_by(course_code = code).all()
        if(data == []):
            new_course = Course(course_code = code, course_name = c_name, course_description = desc)
            db.session.add(new_course)
            db.session.commit()
            return redirect("/courses")
        else:
            return render_template("course_exist.html")

@app.route("/course/<int:course_id>/update", methods = ["GET", "POST"])
def course_update(course_id):
    if request.method == "GET":
        course = Course.query.filter_by(course_id = course_id).first()
        return render_template("course_update.html", course = course)
    else:
        c_name = request.form["c_name"]
        desc = request.form["desc"]
        course = Course.query.filter_by(course_id = course_id).first()
        course.course_name = c_name
        course.course_description = desc
        db.session.commit()
        return redirect("/courses")

@app.route("/course/<int:course_id>/delete")
def course_delete(course_id):
    enroll = Enrollments.query.filter_by(ecourse_id = course_id).all()
    for row in enroll:
        db.session.delete(row)
    course = Course.query.filter_by(course_id = course_id).first()
    db.session.delete(course)
    db.session.commit()
    return redirect("/")

@app.route("/course/<int:course_id>")
def course_display(course_id):
    courses = Course.query.filter_by(course_id = course_id).all()
    enroll = Enrollments.query.filter_by(ecourse_id = course_id).all()
    students = []
    for row in enroll:
        students.append(Student.query.filter_by(student_id = row.estudent_id).first())
    return render_template("course_display.html", students = students, courses = courses)

if __name__ == '__main__':
    app.run()