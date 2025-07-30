from database import get_db_connection
from utils import security
from models.user import UserRegister , UserLogin
import pymysql

def print_all_users():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for row in rows:
                print(row)


def register(register_data: UserRegister):
    hashed_password = security.hash_password(register_data.password)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (register_data.name, register_data.email, hashed_password))
            conn.commit()

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = "SELECT id, name FROM users WHERE email = %s"
                cursor.execute(sql, (register_data.email,))
                user_row = cursor.fetchone()

                if not user_row:
                    return {
                        "success": False,
                        "message": "User creation failed.",
                        "data": None
                    }

                user_id, name = user_row

        token = security.create_jwt(user_id, name, register_data.email)

        return {
            "success": True,
            "message": "User registered.",
            "data": {
                "token": token,
                "name": name
            }
        }

    except pymysql.IntegrityError as e:
        if "Duplicate entry" in str(e):
            return {
                "success": False,
                "message": "Email already exists.",
                "data": None
            }
        return {
            "success": False,
            "message": "Database integrity error.",
            "data": None
        }

    except pymysql.MySQLError as e:
        print("SQL Error:", e)
        return {
            "success": False,
            "message": "SQL insert failed.",
            "data": None
        }

def login(login_data: UserLogin):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                sql = "SELECT id, name, password FROM users WHERE email = %s"
                cursor.execute(sql, (login_data.email,))
                user_row = cursor.fetchone()

                if not user_row:
                    return {
                        "success": False,
                        "message": "Invalid email or password.",
                        "data": None
                    }

                user_id, name, hashed_password = user_row

        # 驗證密碼
        if not security.verify_password(login_data.password, hashed_password):
            return {
                "success": False,
                "message": "Invalid email or password.",
                "data": None
            }

        # 密碼正確，發 token
        token = security.create_jwt(user_id, name, login_data.email)
        print(security.verify_jwt(token))
        return {
            "success": True,
            "message": "Login successful.",
            "data": {
                "token": token,
                "name": name
            }
        }

    except pymysql.MySQLError as e:
        print("SQL Error:", e)
        return {
            "success": False,
            "message": "Database error.",
            "data": None
        }