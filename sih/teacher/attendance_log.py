import mysql.connector
from mysql.connector import Error

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # apna DB user
    password="Oj@svigupt@17",  # apna DB password
    database="adm"
)
cursor = db.cursor(dictionary=True)

# Function to log attendance
def log_attendance(student_id, qr_code, latitude, longitude):
    try:
        query = """
        INSERT INTO attendance_log (student_id, qr_code, latitude, longitude)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (student_id, qr_code, latitude, longitude))
        db.commit()
        print(f"✅ Attendance logged for student_id={student_id}")
    except Error as e:
        print(f"❌ Error logging attendance: {e}")


# Function to fetch all logs
def get_attendance_logs(student_id=None):
    try:
        if student_id:
            cursor.execute(
                "SELECT * FROM attendance_log WHERE student_id=%s ORDER BY timestamp DESC",
                (student_id,)
            )
        else:
            cursor.execute("SELECT * FROM attendance_log ORDER BY timestamp DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"❌ Error fetching logs: {e}")
        return []
