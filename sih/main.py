from flask import Flask, redirect, url_for, render_template
from admin.app import admin_bp
from student.app import student_bp
from teacher.teacher_app import teacher_bp

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)
app.register_blueprint(teacher_bp)

# Default route
@app.route("/")
def index():
    # Now it will look for templates/index.html
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

