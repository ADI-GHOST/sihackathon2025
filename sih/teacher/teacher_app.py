from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
import mysql.connector
from functools import wraps
import datetime
import json
import os
from .db import create_connection

# Create Blueprint
teacher_bp = Blueprint(
    'teacher', __name__,
    url_prefix='/teacher',
    template_folder='templates'
)

# ----------------------------
# Decorator
# ----------------------------
def teacher_required(f):
    """Decorator to ensure a user is logged in as a teacher."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'teacher':
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            return redirect(url_for('teacher.teacher_login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ----------------------------
# Routes
# ----------------------------

@teacher_bp.route('/')
def index():
    return redirect(url_for('teacher.teacher_login_page'))

@teacher_bp.route('/login_page')
def teacher_login_page():
    return render_template('teacher_portal.html')

@teacher_bp.route('/login', methods=['POST'])
def teacher_login_action():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
    conn = create_connection()
    if not conn: 
        return jsonify({'success': False, 'message': 'Database error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Teachers WHERE email = %s AND password = %s", (email, password))
        teacher = cursor.fetchone()
        if teacher:
            session['user_type'] = 'teacher'
            session['user_id'] = teacher['teacher_id']
            session['user_name'] = teacher['name']
            return jsonify({'success': True, 'teacher': {'name': teacher['name'], 'id': teacher['teacher_id']}})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401
    finally:
        if conn.is_connected(): 
            conn.close()

@teacher_bp.route('/logout', methods=['POST'])
def teacher_logout():
    session.clear()
    return jsonify({'success': True})

# ----------------------------
# Teacher API Endpoints
# ----------------------------

@teacher_bp.route('/api/session')
def teacher_session():
    if session.get('user_type') == 'teacher':
        return jsonify({
            'logged_in': True,
            'teacher': { 'id': session.get('user_id'), 'name': session.get('user_name') }
        })
    return jsonify({'logged_in': False})

# ✅ Today’s Attendance (with location + pending status)
@teacher_bp.route("/today_attendance", methods=["GET"])
def today_attendance():
    conn = create_connection()
    if not conn:
        return jsonify({"status": "fail", "message": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.id, s.name, a.date, a.status, a.latitude, a.longitude, a.schedule_id
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE DATE(a.date) = CURDATE()
            ORDER BY a.date DESC
        """)
        records = cursor.fetchall()
        return jsonify(records)
    finally:
        if conn.is_connected():
            conn.close()

# ✅ Update Status (Approve / Deny)
@teacher_bp.route("/update_status/<int:attendance_id>", methods=["POST"])
def update_status(attendance_id):
    data = request.get_json()
    status = data.get("status")
    if status not in ["Present", "Denied"]:
        return jsonify({"status": "fail", "message": "Invalid status"}), 400

    conn = create_connection()
    if not conn:
        return jsonify({"status": "fail", "message": "DB connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)

        # ✅ Update attendance in DB
        cursor.execute("UPDATE attendance SET status=%s WHERE id=%s", (status, attendance_id))
        conn.commit()

        # ✅ Also update attendance_log.json for consistency
        log_file = "attendance_log.json"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        # update last matching record
        for log in reversed(logs):
            if str(log.get("attendance_id")) == str(attendance_id):
                log["status"] = status
                break

        with open(log_file, "w") as f:
            json.dump(logs, f, indent=4)

        return jsonify({"status": "success", "message": f"Attendance marked as {status}"})
    finally:
        if conn.is_connected():
            conn.close()

# ⚠️ Keep your other teacher APIs below (schedule, today_classes, all_classes, etc.)

