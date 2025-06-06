import os

SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "resume_app"

ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin12345"

UPLOAD_FOLDER = "static/resumes"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024