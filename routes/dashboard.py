from flask import Blueprint, render_template, session
from utils import skills_str_to_comma, datetime_to_str, is_expired
from services.job_post_service import get_active_jobs

dashboard_bp = Blueprint('dashboard', __name__)

# DASHBOARD
@dashboard_bp.route('/')
def dashboard():
    jobs = get_active_jobs()
    for i in range(len(jobs)):
        jobs[i]['skills'] = skills_str_to_comma(jobs[i]['skills'])
        jobs[i]['is_expired'] = is_expired(jobs[i]['deadline'])
        jobs[i]['deadline'] = datetime_to_str(jobs[i]['deadline'])

    return render_template(
        'dashboard.jinja',
        jobs=jobs,
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        user_role = session.get('user_role'),
        active_page='dashboard'
    )