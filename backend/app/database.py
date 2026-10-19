import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "shoury"),
    "database": os.getenv("DB_NAME", "handshake_lab1"),
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
