import MySQLdb
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, RECRUITER_NAME, RECRUITER_EMAIL, RECRUITER_PASSWORD, CANDIDATE_NAME, CANDIDATE_EMAIL, CANDIDATE_PASSWORD
from argon2 import PasswordHasher

ph = PasswordHasher()

# CREATE DATABASE IF NOT EXIST
def create_db():
    connection = MySQLdb.connect(
        MYSQL_HOST,
        MYSQL_USER,
        MYSQL_PASSWORD
    )
    cur = connection.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
    connection.commit()
    cur.close()
    connection.close()
    print(f"✅ Database '{MYSQL_DB}' created or already exists.")

def get_connection():
    return MySQLdb.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        cursorclass=MySQLdb.cursors.DictCursor
    )

# CREATE TABLE IF NOT EXIST
def create_table():
    connection = get_connection()
    cur = connection.cursor()

    # User
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('candidate', 'recruiter') NOT NULL DEFAULT 'candidate'
        )
    """)

    # Resume Information
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resume_information (
            id INT PRIMARY KEY AUTO_INCREMENT,
            candidate_id INT,
            file_path VARCHAR(255),
            name_res VARCHAR(100),
            email_res VARCHAR(100),
            designation TEXT,
            companies TEXT,
            location TEXT,
            techtools TEXT,
            jobskills TEXT,
            years_exp TEXT,
            softskill TEXT,
            college TEXT,
            graduation TEXT,
            degree TEXT,
            FOREIGN KEY (candidate_id) REFERENCES user(id) ON DELETE CASCADE
        )
    """)

    # Job Post
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_post (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            job_title VARCHAR(255) NOT NULL,
            experience INT NOT NULL,
            education VARCHAR(255) NOT NULL,
            skills TEXT NOT NULL,
            location VARCHAR(255) NOT NULL,
            deadline DATE NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        )
    """)

    # Application
    cur.execute("""
        CREATE TABLE IF NOT EXISTS application (
            id INT PRIMARY KEY AUTO_INCREMENT,
            resume_id INT,
            jobpost_id INT,
            candidate_id INT,
            gdrive TEXT,
            status ENUM('Rejected', 'In Progress', 'Proceed'),
            score FLOAT,
            recommendation ENUM('Highly Suitable', 'Moderately Suitable', 'Not Suitable'),
            explanation TEXT,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resume_information(id) ON DELETE CASCADE,
            FOREIGN KEY (jobpost_id) REFERENCES job_post(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES user(id) ON DELETE CASCADE
        )
    """)

    connection.commit()
    cur.close()
    connection.close()
    print("✅ All tables created successfully.")
    
# INSERT RECRUITER USER
def create_recruiter_user():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", (RECRUITER_EMAIL,))
    if cursor.fetchone():
        print("⚠️ Recruiter user already exists. Skipping.")
    else:
        hashed_pw = ph.hash(RECRUITER_PASSWORD)
        cursor.execute(
            "INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (RECRUITER_NAME, RECRUITER_EMAIL, hashed_pw, "recruiter")
        )
        connection.commit()
        print("✅ Recruiter user created successfully.")
    cursor.close()
    connection.close()

# INSERT CANDIDATE USER
def create_candidate_user():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE email = %s", (CANDIDATE_EMAIL,))
    if cursor.fetchone():
        print("⚠️ Candidate user already exists. Skipping.")
    else:
        hashed_pw = ph.hash(CANDIDATE_PASSWORD)
        cursor.execute(
            "INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (CANDIDATE_NAME, CANDIDATE_EMAIL, hashed_pw, "candidate")
        )
        connection.commit()
        print("✅ Candidate user created successfully.")
    cursor.close()
    connection.close()

# INSERT JOB_POST
def insert_job_post():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM job_post")
    if cursor.fetchone():
        print("⚠️ Job Post already exists. Skipping.")
    else:
        cursor.execute(
            """INSERT INTO job_post (
                user_id,
                job_title,
                experience,
                education,
                skills,
                location,
                deadline
            ) VALUES (
                1,
                'Software Engineer',
                3,
                'Bachelor of Computer Science',
                'Detail Oriented;; data sharing;; VMware Horizon View 5.x, 6.x, and 7.x;; Microsoft Hyper-V;; Ticket Resolution;; IT consultation;; Mac;; Customer Service;; Project Management;; Windows;; Middleware Integration;; Software Documentation;; Creativity;; project planning;; budgeting;; design',
                'New York, NY',
                '2025-12-31'
            );"""
        )
        connection.commit()
        print("✅ Job Post created successfully.")
    cursor.close()
    connection.close()