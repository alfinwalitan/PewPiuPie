from flask import Blueprint, request, render_template, redirect, url_for, session
from models.db_init import get_connection
from argon2 import PasswordHasher
import re

auth_bp = Blueprint('auth', __name__)
ph = PasswordHasher()

# EMAIL VALIDATION
def is_valid_email(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(regex, email)

# SIGN UP
@auth_bp.route('/signup', methods=['GET', 'POST'])
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
            connection = get_connection()
            cur = connection.cursor()
            cur.execute("SELECT * FROM user WHERE email = %s", (email,))
            if cur.fetchone():
                error = "Email already registered!"
            else:
                hashed_password = ph.hash(password)
                cur.execute(
                    "INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)",
                    (name, email, hashed_password, 'candidate')
                )
                connection.commit()
                cur.close()
                return redirect(url_for('auth.signin'))
            cur.close()

    return render_template('signup.jinja', error=error)


# SIGN IN
@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        cur = get_connection().cursor()
        cur.execute("SELECT * FROM user WHERE email = %s", (email,))
        account = cur.fetchone()
        cur.close()

        if account:
            try:
                ph.verify(account['password'], password)
                session['user_id'] = account['id']
                session['user_name'] = account['name']
                session['user_role'] = account['role']
                session['user_email'] = account['email']

                return redirect(url_for('dashboard.dashboard'))
            except:
                error = "Invalid email or password!"
        else:
            error = "Invalid email or password!"

    return render_template('signin.jinja', error=error)

# LOGOUT
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.signin'))