from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from utils import skills_str_to_list, datetime_to_str
from models.db_init import get_connection
from services.job_post_service import get_job_post

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
        posted_by = session['user_id']

        connection = get_connection()
        cur = connection.cursor()
        cur.execute("""
            INSERT INTO job_post (job_title, experience, education, skills, location, deadline, posted_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (job_title, experience, education, skills, location, deadline, posted_by))
        connection.commit()
        cur.close()

        return redirect(url_for('dashboard.dashboardhrd'))

    return render_template('postjob.jinja', user_name=session.get('user_name'))

# JOB DETAIL
@jobs_bp.route("/job-detail/<int:job_id>/")
def job_detail(job_id):
    job = get_job_post(job_id)

    if not job:
        return "Job not found", 404

    job['skills'] = skills_str_to_list(job['skills'])
    job['deadline'] = datetime_to_str(job['deadline'])

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
    template = "jobdetail_hrd.jinja" if role == 'recruiter' else "jobdetail_pelamar.jinja"
    return render_template(
        template,
        job=job,
        candidates=candidates,
        user_name=session.get('user_name'),
        user_email=session.get('user_email')
    )

# DELETE JOB
@jobs_bp.route('/delete-job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    if 'user_id' not in session or session.get('user_role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 401

    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT * FROM job_post WHERE id = %s", (job_id,))
    job = cur.fetchone()
    if not job:
        cur.close()
        return jsonify({'error': 'Job not found'}), 404

    cur.execute("DELETE FROM job_post WHERE id = %s", (job_id,))
    connection.commit()
    cur.close()

    return jsonify({'message': 'Job deleted successfully'})