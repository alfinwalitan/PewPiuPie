import os
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from argon2 import PasswordHasher
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# DATABASE CONFIGURATION
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'my_app'

mysql = MySQL(app)
ph = PasswordHasher()


# CREATE TABLE IF NOT EXIST
def create_table():
    cur = mysql.connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT PRIMARY KEY AUTO_INCREMENT,
            job_title VARCHAR(255) NOT NULL,
            experience INT NOT NULL,
            education VARCHAR(255) NOT NULL,
            skills TEXT NOT NULL,
            location VARCHAR(255) NOT NULL,
            deadline DATE NOT NULL,
            posted_by INT NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (posted_by) REFERENCES users(id)
        )
    """)
    mysql.connection.commit()
    cur.close()


# CREATE ADMIN USER
# ONLY USE THIS ONE TIME TO CREATE ADMIN USER
# @app.route('/create-admin', methods=['POST'])
# def create_admin():
#     data = request.json
#     name = data.get("name")
#     email = data.get("email")
#     password = data.get("password")

#     if not name or not email or not password:
#         return {"error": "Incomplete data"}, 400

#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cur.execute("SELECT * FROM users WHERE email = %s", (email,))
#     if cur.fetchone():
#         return {"error": "Admin already exists"}, 400

#     hashed_pw = ph.hash(password)
#     cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
#                 (name, email, hashed_pw, "admin"))
#     mysql.connection.commit()
#     cur.close()

#     return {"message": "Admin created successfully"}


# EMAIL VALIDATION
def is_valid_email(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(regex, email)


# SPLASH SCREEN 1
# @app.route('/splash')
# def splash():
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cur.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
#     jobs = cur.fetchall()
#     cur.close()
#     return render_template('splash.jinja', jobs=jobs)


# SPLASH SCREEN 2
@app.route('/')
def splash():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    cur.close()
    return render_template('splash_new.jinja', jobs=jobs)


# SIGN UP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not name or not email or not password or not confirm_password:
            error = "Please fill out all fields."
        elif not is_valid_email(email):
            error = "Invalid email format."
        elif password != confirm_password:
            error = "Passwords do not match!"
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                error = "Email already registered!"
            else:
                hashed_password = ph.hash(password)
                cur.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                    (name, email, hashed_password, 'user')
                )
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('signin'))
            cur.close()

    return render_template('signup.jinja', error=error)


# SIGN IN
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cur.fetchone()
        cur.close()

        if account:
            try:
                ph.verify(account['password'], password)
                session['user_id'] = account['id']
                session['user_name'] = account['name']
                session['user_role'] = account['role']
                session['user_email'] = account['email']

                return redirect(url_for('dashboardhrd' if account['role'] == 'admin' else 'dashboard_pelamar'))
            except:
                error = "Invalid email or password!"
        else:
            error = "Invalid email or password!"

    return render_template('signin.jinja', error=error)


# DASHBOARD HRD
@app.route('/dashboardhrd')
def dashboardhrd():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('signin'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    cur.close()

    return render_template(
        'dashboard_hrd.jinja',
        jobs=jobs,
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        user_role=session.get('user_role'),
        active_page='dashboard'
    )


# POST JOB
@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('signin'))

    if request.method == 'POST':
        job_title = request.form['job_title']
        experience = int(request.form['experience'])
        education = request.form['education']
        skills = request.form['skills']
        location = request.form['location']
        deadline = request.form['deadline']
        posted_by = session['user_id']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO jobs (job_title, experience, education, skills, location, deadline, posted_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (job_title, experience, education, skills, location, deadline, posted_by))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('dashboardhrd'))

    return render_template('postjob.jinja', user_name=session.get('user_name'))


# DASHBOARD USER
@app.route('/dashboardpelamar')
def dashboard_pelamar():
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('signin'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    cur.close()

    return render_template(
        'dashboard_pelamar.jinja',
        jobs=jobs,
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        active_page='dashboard'
    )


# EDIT PROFILE
@app.route('/update-name', methods=['POST'])
def update_name():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    new_name = request.form.get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Name cannot be empty'}), 400

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    mysql.connection.commit()
    cur.close()
    session['user_name'] = new_name
    return jsonify({'message': 'Name updated successfully', 'new_name': new_name})


# MY APPLICATION
@app.route('/applications')
def application_history():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    # DUMMY DATA FOR TESTING
    applications = [
        {
            "designation": "System Engineer",
            "upload_date": "13 April 2025",
            "status": "In Progress",
            "resume_link": "#"
        },
        {
            "designation": "Machine Learning Engineer",
            "upload_date": "19 January 2025",
            "status": "Proceed to Interview",
            "resume_link": "#"
        },
    ]
    return render_template(
    "application.jinja",
    applications=applications,
    user_name=session.get('user_name'),
    user_email=session.get('user_email'),
    active_page='applications'
)


# JOB DETAIL
@app.route("/job-detail/<int:job_id>")
def job_detail(job_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    job = cur.fetchone()
    cur.close()

    if not job:
        return "Job not found", 404

    # DUMMY DATA FOR TESTING
    candidates = [
        {
            'id': 1,
            'name': 'Andi',
            'designation': 'Junior Developer',
            'experience': 'December 2014 to Present',
            'skills': 'Python, Flask',
            'score': 65,
            'recommendation': 'Not Suitable'
        },
        {
            'id': 2,
            'name': 'Budi',
            'designation': 'Developer',
            'experience': 'December 2015 to February 2018',
            'skills': 'Python, Django, Command Prompt, Problem Solving',
            'score': 90,
            'recommendation': 'Highly Suitable'
        }
    ]

    role = session.get('user_role')

    if role == 'admin':
        return render_template(
            "jobdetail_hrd.jinja",
            job=job,
            candidates=candidates,
            user_name=session.get('user_name'),
            user_email=session.get('user_email')
        )
    else:
        return render_template(
            "jobdetail_pelamar.jinja",
            job=job,
            candidates=candidates,
            user_name=session.get('user_name'),
            user_email=session.get('user_email')
        )


# DELETE JOB
@app.route('/delete-job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'hrd']:
        return jsonify({'error': 'Unauthorized'}), 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
    job = cur.fetchone()
    if not job:
        cur.close()
        return jsonify({'error': 'Job not found'}), 404

    cur.execute("DELETE FROM jobs WHERE id = %s", (job_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Job deleted successfully'})


# CONFIGURATION UPLOAD FILE
app.config['UPLOAD_FOLDER'] = 'static/resumes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# UPLOAD RESUME
@app.route("/upload-resume", methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resumeUpload' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['resumeUpload']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash(f'File "{filename}" uploaded successfully!', 'success')
            return redirect(url_for('dashboard_pelamar'))
        else:
            flash('File type not allowed', 'error')
            return redirect(request.url)

    return render_template(
        "upload_resume.jinja",
        user_name=session.get('user_name'),
        user_email=session.get('user_email')
    )

# # UPLOAD RESUME
# @app.route("/upload-resume")
# def upload_resume():
#     return render_template(
#     "upload_resume.jinja",
#     user_name=session.get('user_name'),
#     user_email=session.get('user_email')
# )


# VIEW RESUME
@app.route("/resume")
def view_resume():

    # DUMMY DATA FOR VIEW RESUME
    candidate = {
        "name": "John Doe",
        "score": 76.1,
        "designation": "System Engineer",
        "xai_results": [
            {"desc": "Experience on React", "score": "+2.3"},
            {"desc": "AWS Certification", "score": "+1.8"},
            {"desc": "No Portfolio", "score": "-1.2"}
        ]
    }
    return render_template(
    "view_resume.jinja",
    user_name=session.get('user_name'),
    user_email=session.get('user_email'),
    candidate=candidate,
)

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))


# RUN SERVER
if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True)
