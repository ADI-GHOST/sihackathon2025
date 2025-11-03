from flask import Blueprint, render_template, request, jsonify, send_file, session
import mysql.connector
import json
import os
from datetime import datetime

# Create Blueprint for student
student_bp = Blueprint(
    'student', __name__,
    url_prefix='/student',
    template_folder='templates'
)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="adm"
)
cursor = db.cursor(dictionary=True)

# Routes
@student_bp.route("/")
def home():
    return render_template("full_style.html")

@student_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, password))
    user = cursor.fetchone()
    if user:
        # ✅ Save student session
        session["student_id"] = user["student_id"]
        return jsonify({"status": "success", "user": user})
    else:
        return jsonify({"status": "fail", "message": "Invalid Email or Password"})

# ✅ Mark Attendance with QR + Location
@student_bp.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    if "student_id" not in session:
        return jsonify({"status": "fail", "message": "Unauthorized"}), 403

    data = request.get_json()
    student_id = session["student_id"]         # ✅ from session
    schedule_id = data.get("schedule_id")      # ✅ from QR code
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not schedule_id:
        return jsonify({"status": "fail", "message": "Schedule ID is required"}), 400

    try:
        # ✅ Insert attendance as Pending (teacher will approve/deny)
        cursor.execute(
            """
            INSERT INTO attendance (student_id, schedule_id, date, status, latitude, longitude)
            VALUES (%s, %s, NOW(), 'Pending', %s, %s)
            ON DUPLICATE KEY UPDATE
                date = NOW(),
                latitude = VALUES(latitude),
                longitude = VALUES(longitude),
                status = 'Pending'
            """,
            (student_id, schedule_id, latitude, longitude)
        )
        db.commit()

        # ✅ Save in JSON log for backup
        log_entry = {
            "student_id": student_id,
            "schedule_id": schedule_id,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Pending"
        }

        log_file = "attendance_log.json"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, "w") as f:
            json.dump(logs, f, indent=4)

        return jsonify({"status": "success", "message": "Attendance submitted. Waiting for teacher approval."})

    except Exception as e:
        db.rollback()
        return jsonify({"status": "fail", "message": str(e)}), 500

# ✅ Download JSON Log
@student_bp.route("/download_attendance_log")
def download_attendance_log():
    log_file = "attendance_log.json"
    if os.path.exists(log_file):
        return send_file(log_file, as_attachment=True)
    else:
        return jsonify({"status": "fail", "message": "Log file not found"}), 404

@student_bp.route("/get_schedule")
def get_schedule():
    cursor.execute("SELECT * FROM schedule")
    return jsonify(cursor.fetchall())

@student_bp.route("/get_results/<int:student_id>")
def get_results(student_id):
    cursor.execute("SELECT * FROM results WHERE student_id=%s", (student_id,))
    return jsonify(cursor.fetchall())

@student_bp.route("/get_attendance/<int:student_id>")
def get_attendance(student_id):
    cursor.execute(
        "SELECT * FROM attendance_log WHERE student_id=%s ORDER BY timestamp DESC",
        (student_id,)
    )
    return jsonify(cursor.fetchall())


