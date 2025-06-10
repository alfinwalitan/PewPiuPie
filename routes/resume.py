import os
from utils import skills_str_to_list
from machine_learning import run_system
from services.job_post_service import get_job_post
from flask import Blueprint, request, redirect, url_for, flash, session, render_template, current_app
from werkzeug.utils import secure_filename

resume_bp = Blueprint('resume', __name__)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# UPLOAD RESUME
@resume_bp.route("/job-detail/<int:job_id>/upload-resume", methods=['GET', 'POST'])
def upload_resume(job_id):
    job = get_job_post(job_id)

    job_desc = {
        "Required Designation": job['job_title'],
        "Required Skills": skills_str_to_list(job['skills']),
        "Required Degree": job['education'],
        "Required Years of Experience": job['experience']
    }

    if 'user_id' not in session:
        return redirect(url_for('auth.signin'))

    if request.method == 'POST':
        file = request.files.get('resumeUpload')
        if not file or file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            result = run_system(
                pdf_path=filepath,
                job_desc=job_desc
            )
            print(result)
            flash(f'File "{filename}" uploaded successfully!', 'success')
            return redirect(url_for('dashboard.dashboard_pelamar'))
        else:
            flash('File type not allowed', 'error')
            return redirect(request.url)

    return render_template(
        "upload_resume.jinja",
        job = job,
        user_name=session.get('user_name'),
        user_email=session.get('user_email')
    )

# VIEW RESUME
@resume_bp.route("/resume")
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