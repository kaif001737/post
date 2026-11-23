from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "my_flask_secret_key"

# PostgreSQL Configuration (Neon)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://neondb_owner:npg_gQ21hTGCNmrx@ep-misty-union-begb88em-pooler.c-9.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db = SQLAlchemy(app)


# Student Database Model
class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(20), nullable=False)

    course = db.Column(db.String(100), nullable=False)


# Home Page
@app.route("/")
def index():

    students = Student.query.order_by(Student.id.desc()).all()

    return render_template("index.html", students=students)


# Save Student Data
@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form.get("name", "").strip()

    email = request.form.get("email", "").strip()

    phone = request.form.get("phone", "").strip()

    course = request.form.get("course", "").strip()

    if not all([name, email, phone, course]):
        flash("Please fill all fields.", "error")
        return redirect("/")

    # Check duplicate email
    existing_student = Student.query.filter_by(email=email).first()

    if existing_student:
        flash("Email already registered!", "error")
        return redirect("/")

    # Create student object
    new_student = Student(
        name=name,
        email=email,
        phone=phone,
        course=course
    )

    # Save to PostgreSQL
    try:
        db.session.add(new_student)

        db.session.commit()

        flash("Student registered successfully!", "success")

    except Exception:
        db.session.rollback()

        flash("Something went wrong while saving data.", "error")

    return redirect("/")


# Delete Student
@app.route("/delete/<int:id>", methods=["POST"])
def delete_student(id):

    student = db.session.get(Student, id)

    if student:
        db.session.delete(student)
        db.session.commit()

        flash("Student deleted successfully!", "success")

    return redirect("/")


# Run Application
if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)