from models.db_init import get_connection
from argon2 import PasswordHasher

ph = PasswordHasher()

def get_email(email):
    connection = get_connection()
    cur = connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s", (email,))
    result = cur.fetchone()
    cur.close()
    return result

def create_user(name, email, password, role='candidate'):
    try:
        hashed_password = ph.hash(password)
        connection = get_connection()
        cur = connection.cursor()
        cur.execute(
            "INSERT INTO user (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )
        connection.commit()
        cur.close()
        return True, "User created successfully"
    except Exception as e:
        return False, str(e)
    
def authenticate_user(email, password):
    try:
        account = get_email(email)
        if account and ph.verify(account['password'], password):
            return True, account
        else:
            return False, "Invalid email or password!"
    except Exception as e:
        return False, "Invalid email or password!"