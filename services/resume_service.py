from models.db_init import get_connection
import requests
import json

def get_resume(res_id):
    try:
        connection = get_connection()
        cur = connection.cursor()

        cur.execute(
            "SELECT * FROM resume_information WHERE id = %s", (res_id,)
        )
        res = cur.fetchone()
        cur.close()
        return True, res
    except Exception as e:
        return False, str(e)
    
def insert_resume(res_info, filepath, filename, user_id, name, email):
    try:
        connection = get_connection()
        cur = connection.cursor()

        cur.execute(
            "INSERT INTO resume_information (candidate_id, file_path, filename, name_res, designation, companies, location, email_res, techtools, jobskills, years_exp, softskill, college, graduation, degree) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                user_id,
                filepath,
                filename,
                name, 
                json.dumps(res_info["Designation"]), 
                json.dumps(res_info["Companies worked at"]),
                json.dumps(res_info["Location"]),
                email,
                json.dumps(res_info["Tech Tools"]),
                json.dumps(res_info["Job Specific Skills"]),
                json.dumps(res_info["Years of Experience"]),
                json.dumps(res_info["Soft Skills"]),
                json.dumps(res_info["College Name"]),
                json.dumps(res_info["Graduation Year"]),
                json.dumps(res_info["Degree"])
            )
        )
        res_id = cur.lastrowid
        connection.commit()
        cur.close()
        return True, res_id
    except Exception as e:
        return False, str(e)

def insert_application(res_id, job_id, user_id, gdrive, score, recommendation, explanation, status):
    try:
        connection = get_connection()
        cur = connection.cursor()

        cur.execute(
            "INSERT INTO application (resume_id, jobpost_id, candidate_id, gdrive, score, recommendation, explanation, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (
                res_id,
                job_id,
                user_id,
                gdrive,
                score,
                recommendation,
                explanation,
                status
            )
        )
        app_id = cur.lastrowid
        connection.commit()
        cur.close()
        return True, app_id
    except Exception as e:
        return False, str(e)
    
def get_xai(application_id):
    try:
        connection = get_connection()
        cur = connection.cursor()

        cur.execute(
            "SELECT * FROM xai WHERE application_id = %s", (application_id,)
        )
        application = cur.fetchone()
        cur.close()
        return True, application
    except Exception as e:
        return False, str(e)
    
def check_drive_link(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)

        # Check if it's a Google sign-in page or forbidden
        if "accounts.google.com" in response.url or response.status_code in [403, 401]:
            return False, "Link is not publicly accessible"

        # check for a generic title in Drive private pages
        if "Google Drive - Sign in" in response.text or "You need access" in response.text:
            return False, "Access is restricted"
        
        return True, "Accessible"
    except requests.RequestException as e:
        return False, f"Error: {str(e)}"
    
def update_application(application_id, new_status):
    try:
        connection = get_connection()
        cur = connection.cursor()

        cur.execute("SELECT id FROM application WHERE id = %s", (application_id,))
        if cur.fetchone() is None:
            return False, "Application not found"
        
        cur.execute(
            "UPDATE application SET status = %s WHERE id = %s", (new_status, application_id)
        )
        connection.commit()
        cur.close()
        return True, f"Status Updated: {new_status}"
    except Exception as e:
        return False, str(e)