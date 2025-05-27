from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from argon2 import PasswordHasher

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# DATABASE CONFIGURATION
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'my_app'

mysql = MySQL(app)
ph = PasswordHasher()

# CREATE TABLE
def create_table():
    cur = mysql.connection.cursor()
    
    # Tabel users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
    """)
    
    # Tabel jobs
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

# SIGN UP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('signup.jinja', error="Passwords do not match!")

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cur.fetchone()

        if account:
            return render_template('signup.jinja', error="Email already registered!")

        hashed_password = ph.hash(password)

        cur.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, 'user')
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('signin'))

    return render_template('signup.jinja', error=None)

# SIGN IN
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cur.fetchone()
        cur.close()

        if account:
            try:
                ph.verify(account['password'], password)

                # Simpan data ke session
                session['user_id'] = account['id']
                session['user_name'] = account['name']
                session['user_role'] = account['role']

                if account['role'] == 'admin':
                    return redirect(url_for('dashboardhrd'))
                else:
                    return redirect(url_for('dashboard_pelamar'))

            except:
                return render_template('signin.jinja', error="Invalid email or password!")
        else:
            return render_template('signin.jinja', error="Invalid email or password!")

    return render_template('signin.jinja', error=None)

# DASHBOARD HRD (Admin)
@app.route('/dashboardhrd')
def dashboardhrd():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    cur.close()

    return render_template('dashboard_hrd.jinja', jobs=jobs, user_name=session.get('user_name'))

# POST JOB
@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        job_title = request.form['job_title']
        experience = int(request.form['experience'])
        education = request.form['education']
        skills = request.form['skills']
        location = request.form['location']
        deadline = request.form['deadline']
        posted_by = session['user_id']  # ambil user id dari session

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
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    cur.close()

    return render_template('dashboard_pelamar.jinja', jobs=jobs, user_name=session.get('user_name'), active_page='dashboard')

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

# MY APPLICATION
@app.route('/applications')
def application_history():

    # Dummy data for testing, will be replace later
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
    return render_template("application.jinja", applications=applications, user_name=session.get('user_name'), active_page='applications')

# RUN
if __name__ == '__main__':
    with app.app_context():
        create_table()
    app.run(debug=True)
