from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template
from models.db_init import get_connection

user_bp = Blueprint('user', __name__)

# EDIT PROFILE
@user_bp.route('/update-name', methods=['POST'])
def update_name():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    new_name = request.form.get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Name cannot be empty'}), 400

    user_id = session['user_id']
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
    connection.commit()
    cur.close()
    session['user_name'] = new_name
    return jsonify({'message': 'Name updated successfully', 'new_name': new_name})

# APPLICATION HISTORY
@user_bp.route('/applications')
def application_history():
    if 'user_id' not in session:
        return redirect(url_for('auth.signin'))

    # DUMMY DATA FOR TESTING
    applications = [
        {
            "designation": "System Engineer",
            "upload_date": "13 April 2025",
            "status": "In Progress",
            "resume_link": "#"
        },
        {
            "designation": "Machine Learning Engineer",
            "upload_date": "19 January 2025",
            "status": "Proceed to Interview",
            "resume_link": "#"
        },
    ]
    return render_template(
    "application.jinja",
    applications=applications,
    user_name=session.get('user_name'),
    user_email=session.get('user_email'),
    user_role=session.get('user_role'),
    active_page='applications'
)