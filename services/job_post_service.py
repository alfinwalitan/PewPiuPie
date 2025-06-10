from models.db_init import get_connection

def get_job_post(job_id):
    connection = get_connection()
    cur = connection.cursor()

    cur.execute("SELECT * FROM job_post WHERE id = %s", (job_id,))
    job = cur.fetchone()
    cur.close()

    return job