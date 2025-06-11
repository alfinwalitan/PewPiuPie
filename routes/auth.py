from flask import Blueprint, request, render_template, redirect, url_for, session
from services.auth_service import get_email, create_user, authenticate_user
import re

auth_bp = Blueprint('auth', __name__)

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
        elif get_email(email) is not None:
            error = "Email already registered!"
        else:
            success, message = create_user(name, email, password)
            if success:
                return redirect(url_for('auth.signin'))
            else:
                error = f"Error: {message}"

    return render_template('signup.jinja', error=error)


# SIGN IN
@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        success, result = authenticate_user(email, password)

        if success:
            account = result
            session['user_id'] = account['id']
            session['user_name'] = account['name']
            session['user_role'] = account['role']
            session['user_email'] = account['email']

            return redirect(url_for('dashboard.dashboard'))
        else:
            error = result

    return render_template('signin.jinja', error=error)

# LOGOUT
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.signin'))