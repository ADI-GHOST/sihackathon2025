USE adm;

-- Students table
CREATE TABLE IF NOT EXISTS students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  password VARCHAR(100)
);

-- Sample users
INSERT INTO students (name, email, password) VALUES 
('Mradul Goyal','mradul@example.com','12345'),
('Rashmi Sharma','rashmi@example.com','abc123');

-- Schedule table
CREATE TABLE IF NOT EXISTS schedule (
  id INT AUTO_INCREMENT PRIMARY KEY,
  day VARCHAR(50),
  time VARCHAR(50),
  subject VARCHAR(100)
);

INSERT INTO schedule (day, time, subject) VALUES
('Monday','9:00 - 11:00','Mathematics'),
('Tuesday','10:00 - 12:00','Physics'),
('Wednesday','11:00 - 1:00','Chemistry');

-- Results table
CREATE TABLE IF NOT EXISTS results (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  subject VARCHAR(100),
  marks INT,
  grade VARCHAR(5),
  FOREIGN KEY (student_id) REFERENCES students(student_id)
);

INSERT INTO results (student_id, subject, marks, grade) VALUES
(1,'Math',88,'A'),
(1,'Physics',79,'B+'),
(1,'Chemistry',92,'A+'),
(2,'Math',75,'B'),
(2,'Physics',85,'A'),
(2,'Chemistry',80,'B+');

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(20),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- ✅ Attendance Log Table
CREATE TABLE IF NOT EXISTS attendance_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  qr_code VARCHAR(255),
  latitude DECIMAL(10,8),
  longitude DECIMAL(11,8),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id)
);
