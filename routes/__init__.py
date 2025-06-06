from .auth import auth_bp
from .dashboard import dashboard_bp
from .jobs import jobs_bp
from .resume import resume_bp
from .user import user_bp

all_blueprints = [auth_bp, dashboard_bp, jobs_bp, resume_bp, user_bp]