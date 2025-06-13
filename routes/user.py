from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template, flash
from services.user_service import get_user, edit_profile, get_user_applications
from utils import datetime_to_str

user_bp = Blueprint('user', __name__)

# GET USER NAME
@user_bp.route('/get-user-info', methods=['GET'])
def get_user_info():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']
    success, user = get_user(user_id)

    if not success:
        return jsonify({'error': "User Not Found"}), 404

    return jsonify({
        'name': user['name'],
        'email': user['email']
    })

# EDIT PROFILE
@user_bp.route('/update-name', methods=['POST'])
def update_name():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    new_name = request.form.get('name', '').strip()
    if not new_name:
        return jsonify({'error': 'Name cannot be empty'}), 400

    user_id = session['user_id']
    success, message = edit_profile(user_id, new_name)
    if not success:
        return jsonify({'error': message}), 500
    session['user_name'] = new_name
    return jsonify({'message': 'Name updated successfully', 'new_name': new_name})


# APPLICATION HISTORY
@user_bp.route('/applications')
def application_history():
    if 'user_id' not in session or session.get('user_role') != 'candidate':
        return redirect(url_for('auth.signin'))
    
    user_id = session.get('user_id')
    success, applications = get_user_applications(user_id)

    if not success:
        return jsonify({'error': applications}), 404
    
    for app in applications:
        app['application_date'] = datetime_to_str(app['application_date'])

    return render_template(
    "application.jinja",
    applications=applications,
    user_name=session.get('user_name'),
    user_email=session.get('user_email'),
    user_role=session.get('user_role'),
    active_page='applications'
)