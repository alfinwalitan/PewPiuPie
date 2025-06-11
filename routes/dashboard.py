from flask import Blueprint, render_template, session, redirect, url_for
from utils import skills_str_to_comma, datetime_to_str
from models.db_init import get_connection

dashboard_bp = Blueprint('dashboard', __name__)

# # SPLASH SCREEN 2
# @dashboard_bp.route('/')
# def splash():
#     cur = get_connection().cursor()
#     cur.execute("SELECT * FROM job_post ORDER BY posted_at DESC")
#     jobs = cur.fetchall()
#     cur.close()
#     return render_template('dashboard_pelamar.jinja', jobs=jobs)

# # DASHBOARD HRD
# @dashboard_bp.route('/dashboardhrd')
# def dashboardhrd():
#     if 'user_id' not in session or session.get('user_role') != 'recruiter':
#         return redirect(url_for('auth.signin'))

#     cur = get_connection().cursor()
#     cur.execute("SELECT * FROM job_post ORDER BY posted_at DESC")
#     jobs = cur.fetchall()

#     for i in range(len(jobs)):
#         jobs[i]['skills'] = skills_str_to_comma(jobs[i]['skills'])
#         jobs[i]['deadline'] = datetime_to_str(jobs[i]['deadline'])
#     cur.close()

#     return render_template(
#         'dashboard_hrd.jinja',
#         jobs=jobs,
#         user_name=session.get('user_name'),
#         user_email=session.get('user_email'),
#         user_role=session.get('user_role'),
#         active_page='dashboard'
#     )

# # DASHBOARD USER
# @dashboard_bp.route('/dashboardpelamar')
# def dashboard_pelamar():
#     if 'user_id' not in session or session.get('user_role') != 'candidate':
#         return redirect(url_for('auth.signin'))

#     cur = get_connection().cursor()
#     cur.execute("SELECT * FROM job_post ORDER BY posted_at DESC")
#     jobs = cur.fetchall()
#     for i in range(len(jobs)):
#         jobs[i]['skills'] = skills_str_to_comma(jobs[i]['skills'])
#         jobs[i]['deadline'] = datetime_to_str(jobs[i]['deadline'])
#     cur.close()

#     return render_template(
#         'dashboard_pelamar.jinja',
#         jobs=jobs,
#         user_name=session.get('user_name'),
#         user_email=session.get('user_email'),
#         active_page='dashboard'
#     )

# DASHBOARD USER
@dashboard_bp.route('/')
def dashboard():
    cur = get_connection().cursor()
    cur.execute("SELECT * FROM job_post ORDER BY posted_at DESC")
    jobs = cur.fetchall()
    for i in range(len(jobs)):
        jobs[i]['skills'] = skills_str_to_comma(jobs[i]['skills'])
        jobs[i]['deadline'] = datetime_to_str(jobs[i]['deadline'])
    cur.close()

    return render_template(
        'dashboard.jinja',
        jobs=jobs,
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        user_role = session.get('user_role'),
        active_page='dashboard'
    )