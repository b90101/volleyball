from database import get_db_connection
from utils import security
from models.user import UserRegister
import pymysql

def print_all_users():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for row in rows:
                print(row)


def register(user: UserRegister):
    hashed_password = security.hash_password(user.password)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (user.name, user.email, hashed_password))
                user_id = cursor.lastrowid
            conn.commit()

        token = security.create_jwt(user_id, user.name, user.email)

        return {
            "success": True,
            "message": "User registered.",
            "data": {
                "token": token,
                "name": user.name
            }
        }

    except pymysql.MySQLError as e:
        print("SQL Error:", e)
        return {
            "success": False,
            "message": "SQL insert failed.",
            "data": None
        }
