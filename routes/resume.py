import os
import uuid
from utils import skills_str_to_list
from machine_learning import run_system
from services.job_post_service import get_job_post
from services.resume_service import insert_resume, insert_application, insert_xai, check_drive_link
from flask import Blueprint, request, redirect, url_for, flash, session, render_template, current_app, jsonify
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
    user_id = session['user_id']

    if request.method == 'POST':
        file = request.files.get('resumeUpload')
        gdrive = request.form['gdriveLink'].strip()

        is_accessible, message = check_drive_link(gdrive)
        link = None
        if gdrive:
            if is_accessible:
                link = gdrive
            else:
                flash(message, 'error')

        if not file or file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
            flash('File too large.', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            # Analyze Resume
            success, result = run_system(
                pdf_path=filepath,
                job_desc=job_desc
            )

            if success:
                resume_success, res_id = insert_resume(
                    res_info=result['Resume Information'],
                    filepath=filepath,
                    user_id=user_id,
                    name=session['user_name'],
                    email=session['user_email']
                )

                if not resume_success:
                    return jsonify({'error': res_id}), 500
                
                application_success, application_result = insert_application(
                    res_id=res_id,
                    job_id=job_id,
                    user_id=user_id,
                    gdrive=link,
                    score=result['Score'],
                    recommendation=result['Resume Classification']
                )

                if not application_success:
                    return jsonify({'error': application_result}), 500
                
                xai_success, xai_error = insert_xai(
                    application_id=application_result,
                    explanation=result['Summary']
                )

                if not xai_success:
                    return jsonify({'error': xai_error}), 500

                flash(f'File "{filename}" uploaded successfully!', 'success')
                return redirect(url_for('dashboard.dashboard'))
        else:
            flash('File type not allowed', 'error')
            return redirect(request.url)

    return render_template(
        "upload_resume.jinja",
        job = job,
        user_name=session.get('user_name'),
        user_email=session.get('user_email'),
        user_role=session.get('user_role')
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
    user_role=session.get('user_role'),
    candidate=candidate,
)