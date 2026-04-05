import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "appuser"),
            password=os.getenv("DB_PASSWORD", "app123"),
            database=os.getenv("DB_NAME", "job_notification_db")
        )
        return conn
    except Error as e:
        print(f"[DB ERROR] Could not connect to MySQL: {e}")
        raise
