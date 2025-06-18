from services.job_post_service import get_job_post, insert_job_post, delete_job_by_id, get_job_applications, already_applied
from services.resume_service import get_resume
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from utils import skills_str_to_list, datetime_to_str, load_json, is_expired

jobs_bp = Blueprint('jobs', __name__)

# POST JOB
@jobs_bp.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session or session.get('user_role') != 'recruiter':
        return redirect(url_for('auth.signin'))

    if request.method == 'POST':
        job_title = request.form['job_title']
        experience = int(request.form['experience'])
        education = request.form['education']
        skills = request.form['skills']
        location = request.form['location']
        deadline = request.form['deadline']
        user_id = session['user_id']
        auto_reject = True if request.form['autoReject'] == "TRUE" else False

        success, message = insert_job_post(job_title, experience, education, skills, location, deadline, auto_reject, user_id)
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash(f"Error: {message}", "error")
            return redirect(request.url)

    return render_template(
        'postjob.jinja', 
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        user_role = session.get('user_role')
    )

# JOB DETAIL
@jobs_bp.route("/job-detail/<int:job_id>/")
def job_detail(job_id):
    job = get_job_post(job_id)

    if not job:
        return "Job not found", 404
    
    apply_success, can_apply = already_applied(session.get('user_id'), job_id)
    if apply_success:
        job['can_apply'] = can_apply
    else:
        return "Internal Server Error", 500

    job['skills'] = skills_str_to_list(job['skills'])
    job['is_expired'] = is_expired(job['deadline'])
    job['deadline'] = datetime_to_str(job['deadline'])

    role = session.get('user_role')
    success, applications = get_job_applications(job_id)
    if success and applications:
        for i in range(len(applications)):
            res_success, resume = get_resume(applications[i]['resume_id'])
            if res_success:
                applications[i]['name'] = resume['name_res']
                applications[i]['email'] = resume['email_res']
                applications[i]['designation'] = load_json(resume['designation'])
        applications = applications if role == 'recruiter' else None
    else:
        applications = None

    return render_template(
        "jobdetail.jinja",
        job=job,
        applications=applications,
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        user_role = session.get('user_role')
    )

# DELETE JOB
@jobs_bp.route('/delete-job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    if 'user_id' not in session or session.get('user_role') != 'recruiter':
        return redirect(url_for('auth.signin'))

    success, message = delete_job_by_id(job_id)
    if not success:
        return jsonify({'error': message}), 404

    flash(message, 'success')
    return jsonify({'message': message}), 200