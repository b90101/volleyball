from database import get_db_connection
from utils import security
from models.user import UserRegister , UserLogin , UserUpdate
import pymysql

def print_all_users():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for row in rows:
                print(row)


def register(register_data: UserRegister) -> dict :
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

def login(login_data: UserLogin) -> dict :
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


def update(payload: dict, update_data: UserUpdate) -> dict:
    user_id = payload.get("user_id")
    if not user_id:
        return {
            "success": False,
            "message": "Missing user ID.",
            "data": None
        }

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 查詢目前的使用者資料
                cursor.execute("SELECT name, email FROM users WHERE id = %s", (user_id,))
                current_user = cursor.fetchone()

                if not current_user:
                    return {
                        "success": False,
                        "message": "User not found.",
                        "data": None
                    }

                current_name, current_email = current_user

                # 比對有沒有變動
                if (
                    (update_data.name is None or update_data.name == current_name)
                    and
                    (update_data.email is None or update_data.email == current_email)
                ):
                    return {
                        "success": True,
                        "message": "No changes detected.",
                        "data": None
                    }

                # 開始準備 update 語句
                fields = []
                values = []

                if update_data.name is not None and update_data.name != current_name:
                    fields.append("name = %s")
                    values.append(update_data.name)

                if update_data.email is not None and update_data.email != current_email:
                    fields.append("email = %s")
                    values.append(update_data.email)

                values.append(user_id)

                sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
                cursor.execute(sql, tuple(values))
            conn.commit()

        return {
            "success": True,
            "message": "User info updated.",
            "data": {
                "name": update_data.name or current_name,
                "email": update_data.email or current_email
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