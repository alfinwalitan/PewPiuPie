import MySQLdb
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, ADMIN_EMAIL, ADMIN_NAME, ADMIN_PASSWORD
from argon2 import PasswordHasher

ph = PasswordHasher()

# CREATE DATABASE IF NOT EXIST
def create_db():
    connection = MySQLdb.connect(
        MYSQL_HOST,
        MYSQL_USER,
        MYSQL_PASSWORD
    )
    cur = connection.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
    connection.commit()
    cur.close()
    connection.close()
    print(f"✅ Database '{MYSQL_DB}' created or already exists.")

def get_connection():
    return MySQLdb.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASSWORD,
        db=MYSQL_DB,
        cursorclass=MySQLdb.cursors.DictCursor
    )

# CREATE TABLE IF NOT EXIST
def create_table():
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INT PRIMARY KEY AUTO_INCREMENT,
            job_title VARCHAR(255) NOT NULL,
            experience INT NOT NULL,
            education VARCHAR(255) NOT NULL,
            skills TEXT NOT NULL,
            location VARCHAR(255) NOT NULL,
            deadline DATE NOT NULL,
            posted_by INT NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (posted_by) REFERENCES users(id)
        )
    """)
    connection.commit()
    cur.close()
    connection.close()
    
# INSERT ADMIN USER
def create_admin_user():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (ADMIN_EMAIL,))
    if cursor.fetchone():
        print("⚠️ Admin user already exists. Skipping.")
    else:
        hashed_pw = ph.hash(ADMIN_PASSWORD)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (ADMIN_NAME, ADMIN_EMAIL, hashed_pw, "admin")
        )
        connection.commit()
        print("✅ Admin user created successfully.")
    cursor.close()
    connection.close()