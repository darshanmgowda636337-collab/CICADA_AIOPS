# ==========================================================
# CICADA AIOPS - MYSQL DATABASE CONNECTION
# ==========================================================

import mysql.connector
from mysql.connector import Error

from config import Config


# ==========================================================
# GET DATABASE CONNECTION
# ==========================================================

def get_db_connection():

    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            charset="utf8mb4",
            use_unicode=True,
            connection_timeout=10
        )

        if connection.is_connected():
            print("[CICADA] MySQL connected successfully.")
            return connection

    except Error as error:
        print(f"[MYSQL ERROR] {error}")

    return None


# ==========================================================
# TEST DATABASE CONNECTION
# ==========================================================

def test_db_connection():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()

        if connection is None:
            return False

        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT DATABASE() AS database_name")

        result = cursor.fetchone()

        print("[SUCCESS] MySQL connection verified.")
        print("[DATABASE]", result["database_name"])

        return True

    except Error as error:
        print("[DATABASE ERROR]", error)
        return False

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()