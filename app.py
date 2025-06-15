from flask import Flask
from config import *
from models.db_init import create_db, create_table, create_recruiter_user, create_candidate_user, insert_job_post
from routes import all_blueprints

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

for bp in all_blueprints:
    app.register_blueprint(bp)

# RUN SERVER
if __name__ == '__main__':
    with app.app_context():
        create_db()
        create_table()
        create_recruiter_user()
        create_candidate_user()
        insert_job_post()
    app.run(host="0.0.0.0", port=5000, debug=True)
