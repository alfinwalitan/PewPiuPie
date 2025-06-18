from models.db_init import get_connection

def get_user(user_id):
    try:
        connection = get_connection()
        cur = connection.cursor()
        cur.execute("SELECT name, email FROM user WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return True, user
    except Exception as e:
        return False, str(e)

def edit_profile(user_id, new_name):
    try:
        connection = get_connection()
        cur = connection.cursor()
        cur.execute("UPDATE user SET name = %s WHERE id = %s", (new_name, user_id))
        connection.commit()
        cur.close()

        return True, "Name updated successfully"
    except Exception as e:
        return False, str(e)
    
def get_user_applications(user_id):
    try:
        connection = get_connection()
        cur = connection.cursor()
        cur.execute("""
                    SELECT application.status, application.application_date, resume.file_path, resume.filename, job_post.job_title FROM application 
                    JOIN resume ON application.resume_id = resume.id
                    JOIN job_post ON application.jobpost_id = job_post.id
                    WHERE application.user_id = %s
        """, (user_id,)
        )
        applications = cur.fetchall()
        cur.close()
        return True, applications
    except Exception as e:
        return False, str(e)