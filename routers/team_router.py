from database import get_db_connection
from utils import security
from models.team import TeamRegister
import pymysql
import datetime

def row_to_dict(row: tuple, description: tuple) -> dict:
    """
    將資料庫查詢結果的 row 轉成 dict。
    - row: 資料列 (tuple)
    - description: cursor.description 傳回的欄位資訊
    """
    keys = [col[0] for col in description]
    return {key: (str(value) if isinstance(value, (datetime.datetime, datetime.date)) else value) 
            for key, value in zip(keys, row)}

def register(payload: dict, register_data: TeamRegister) -> dict:
    user_id = payload["user_id"]

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 1. 插入球隊資料
                sql_insert_team = """
                    INSERT INTO teams (name, description, creator_id)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql_insert_team, (register_data.name, register_data.description, user_id))
                team_id = cursor.lastrowid

                # 2. 插入 team_members，紀錄建立者為隊長
                sql_insert_member = """
                    INSERT INTO team_members (team_id, user_id, role)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql_insert_member, (team_id, user_id, "captain"))

                # 3. 提交
                conn.commit()

                # 4. 查詢剛剛建立的球隊資料
                sql_select = "SELECT id, name, description, creator_id, created_at FROM teams WHERE id = %s"
                cursor.execute(sql_select, (team_id,))
                row = cursor.fetchone()

                if not row:
                    return {
                        "success": False,
                        "message": "Team creation failed to verify.",
                        "data": None
                    }

                team = row_to_dict(row, cursor.description)

        return {
            "success": True,
            "message": "Team created successfully.",
            "data": team
        }

    except pymysql.MySQLError as e:
        print("SQL Error:", e)
        return {
            "success": False,
            "message": "Database error during team creation.",
            "data": None
        }

def add_team_members():
    pass