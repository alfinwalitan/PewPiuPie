from models.db_init import get_connection

def get_job_post(job_id):
    connection = get_connection()
    cur = connection.cursor()

    cur.execute("SELECT * FROM job_post WHERE id = %s", (job_id,))
    job = cur.fetchone()
    cur.close()

    return job

def insert_job_post(job_title, experience, education, skills, location, deadline, user_id):
    try:
        connection = get_connection()
        cur = connection.cursor()
        cur.execute("""
            INSERT INTO job_post (job_title, experience, education, skills, location, deadline, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (job_title, experience, education, skills, location, deadline, user_id))
        connection.commit()
        cur.close()
        return True, "Job Post Created Successfully"
    except Exception as e:
        return False, str(e)

def delete_job_by_id(job_id):
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT * FROM job_post WHERE id = %s", (job_id,))
    job = cur.fetchone()

    if not job:
        cur.close()
        return False, "Job not found"

    cur.execute("DELETE FROM job_post WHERE id = %s", (job_id,))
    connection.commit()
    cur.close()
    return True, "Job deleted successfully"

def get_active_jobs():
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT * FROM job_post ORDER BY deadline ASC")
    jobs = cur.fetchall()
    cur.close()
    return jobs