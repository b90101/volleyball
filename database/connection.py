import os
import pymysql
from dotenv import load_dotenv
from contextlib import contextmanager 

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

@contextmanager
def get_db_connection():
    conn = pymysql.connect(host=DB_HOST, port=3306, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, charset='utf8mb4')
    try:
        yield conn
    finally:
        conn.close()
