import os
import uuid
from utils import skills_str_to_list, format_explanation, load_json, create_unique_list
from machine_learning import run_system
from services.job_post_service import get_job_post, get_application
from services.resume_service import insert_resume, insert_application, check_drive_link, get_resume, update_application
from flask import Blueprint, request, redirect, url_for, flash, session, render_template, current_app, jsonify
from werkzeug.utils import secure_filename

resume_bp = Blueprint('resume', __name__)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# UPLOAD RESUME
@resume_bp.route("/job-detail/<int:job_id>/upload-resume", methods=['GET', 'POST'])
def upload_resume(job_id):
    if 'user_id' not in session or session.get('user_role') != 'candidate':
        return redirect(url_for('auth.signin'))
    
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
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename).replace("\\", "/")
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
                    filename=filename,
                    user_id=user_id,
                    name=session['user_name'],
                    email=session['user_email']
                )

                if not resume_success:
                    return jsonify({'error': res_id}), 500
                
                status = "In Progress"
                if result['Resume Classification'] == "Not Suitable":
                    status = "Rejected"
                
                application_success, application_result = insert_application(
                    res_id=res_id,
                    job_id=job_id,
                    user_id=user_id,
                    gdrive=link,
                    score=result['Score'],
                    recommendation=result['Resume Classification'],
                    explanation=result['Summary'],
                    status=status
                )

                if not application_success:
                    return jsonify({'error': application_result}), 500

                flash(f'File "{filename}" uploaded successfully!', 'success')
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash("Internal Server Error", 'error')
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
@resume_bp.route("/resume/<int:application_id>")
def view_resume(application_id):
    if 'user_id' not in session or session.get('user_role') != 'recruiter':
        return redirect(url_for('auth.signin'))
    
    candidate = {}
    application_success, application = get_application(application_id)
    if application_success:
        candidate['application_id'] = application_id
        candidate['score'] = application['score']
        candidate['recommendation'] = application['recommendation']
        candidate['summary'] = format_explanation(application['explanation'])
        candidate['gdrive'] = application['gdrive']

        res_id = application['resume_id']
        resume_success, res = get_resume(res_id)
    
        if resume_success:
            years_exp = load_json(res['years_exp'])
            res_designation = load_json(res['designation'])
            combined = [d for d in years_exp if d.get('designation')]
            combined += [{'exp_range': "-", 'designation': des} for des in res_designation]

            seen = set()
            unique_exp = []
            for item in combined:
                key = item['designation'].lower()  # case-insensitive check
                if key not in seen:
                    seen.add(key)
                    unique_exp.append(item)

            skills = load_json(res['jobskills']) + load_json(res['techtools'])

            candidate['name'] = res['name_res']
            candidate['email'] = res['email_res']
            candidate['filepath'] = res['file_path'].replace('static/', "")
            candidate['skills'] = create_unique_list(skills)
            candidate['softskills'] = create_unique_list(load_json(res['softskill']))
            candidate['education'] = load_json(res['degree'])
            candidate['experience'] = unique_exp
            candidate['companies'] = load_json(res['companies'])
            candidate['college'] = load_json(res['college'])
            candidate['graduation'] = load_json(res['graduation'])

    return render_template(
    "view_resume.jinja",
    user_name=session.get('user_name'),
    user_email=session.get('user_email'),
    user_role=session.get('user_role'),
    candidate=candidate,
)

# UPDATE STATUS
@resume_bp.route("/update-status/<int:application_id>", methods=['POST'])
def update_status(application_id):
    if 'user_id' not in session or session.get('user_role') != 'recruiter':
        return redirect(url_for('auth.signin'))
    
    new_status = request.json.get('status')
    if new_status not in ['Rejected', 'In Progress', 'Proceed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    success, message = update_application(application_id, new_status)
    print(message)
    if not success:
        return jsonify({'error': message}), 404

    flash(message, 'success')
    return jsonify({'message': message}), 200