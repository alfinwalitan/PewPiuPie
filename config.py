import os

SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "resume_app"

RECRUITER_NAME = "Recruiter"
RECRUITER_EMAIL = "recruiter@example.com"
RECRUITER_PASSWORD = "recruiter12345"

CANDIDATE_NAME = "Candidate"
CANDIDATE_EMAIL = "candidate@example.com"
CANDIDATE_PASSWORD = "candidate12345"

UPLOAD_FOLDER = "static/resumes"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024