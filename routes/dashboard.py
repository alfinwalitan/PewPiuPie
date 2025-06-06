from flask import Blueprint, render_template, session, redirect, url_for
from models.db_init import get_connection

dashboard_bp = Blueprint('dashboard', __name__)

# SPLASH SCREEN 2
@dashboard_bp.route('/')
def splash():
    cur = get_connection().cursor()
    cur.execute("SELECT * FROM jobs ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    cur.close()
    return render_template('splash_new.jinja', jobs=jobs)

# DASHBOARD HRD
@dashboard_bp.route('/dashboardhrd')
def dashboardhrd():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return redirect(url_for('auth.signin'))

    cur = get_connection().cursor()
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

# DASHBOARD USER
@dashboard_bp.route('/dashboardpelamar')
def dashboard_pelamar():
    if 'user_id' not in session or session.get('user_role') != 'user':
        return redirect(url_for('auth.signin'))

    cur = get_connection().cursor()
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