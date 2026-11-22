# ==========================================================
# CICADA AIOPS - BACKEND DATABASE OPERATIONS
# ==========================================================

from mysql.connector import Error

from database.db_connection import get_db_connection


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    return get_db_connection()


# ==========================================================
# CHECK DATABASE
# ==========================================================

def check_database():

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return False

        cursor = connection.cursor()
        cursor.execute("SELECT 1")

        return cursor.fetchone() is not None

    except Error as error:
        print("[DATABASE CHECK ERROR]", error)
        return False

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================================
# GET TELEMETRY
# ==========================================================

def get_telemetry(limit=100):

    connection = None
    cursor = None

    try:
        limit = max(1, min(int(limit), 1000))

        connection = get_connection()

        if connection is None:
            return []

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM telemetry LIMIT %s",
            (limit,)
        )

        return cursor.fetchall()

    except Error as error:
        print("[TELEMETRY ERROR]", error)
        return []

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================================
# GET INCIDENTS
# ==========================================================

def get_incidents():

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return []

        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM incidents")

        return cursor.fetchall()

    except Error as error:
        print("[INCIDENT ERROR]", error)
        return []

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            # ==========================================================
# INSERT TELEMETRY INTO MYSQL
# ==========================================================

import json


def insert_telemetry(data):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            print("[CICADA] Database unavailable")
            return None

        cursor = connection.cursor(dictionary=True)

        # Get actual telemetry table columns
        cursor.execute("SHOW COLUMNS FROM telemetry")
        table_columns = {
            row["Field"] for row in cursor.fetchall()
        }

        # Prepare values using columns that actually exist
        values = {}

        for key, value in data.items():

            if key in table_columns:

                if key == "metadata":
                    value = json.dumps(value)

                values[key] = value

        if not values:
            raise ValueError(
                "No matching columns found in telemetry table"
            )

        columns = list(values.keys())

        column_names = ", ".join(
            f"`{column}`" for column in columns
        )

        placeholders = ", ".join(
            ["%s"] * len(columns)
        )

        query = f"""
            INSERT INTO telemetry ({column_names})
            VALUES ({placeholders})
        """

        cursor.execute(
            query,
            tuple(values[column] for column in columns)
        )

        connection.commit()

        record_id = cursor.lastrowid

        print(
            f"[CICADA] Telemetry inserted successfully: {record_id}"
        )

        return record_id

    except Exception as error:

        if connection:
            connection.rollback()

        print("[TELEMETRY INSERT ERROR]", error)

        return None

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            # ==========================================================
# USER REGISTRATION
# ==========================================================

def create_user(username, email, password_hash):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return None

        cursor = connection.cursor()

        query = """
            INSERT INTO users
            (username, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (username, email, password_hash, "user")
        )

        connection.commit()

        user_id = cursor.lastrowid

        print("[CICADA] User registered:", user_id)

        return user_id

    except Error as error:

        if connection:
            connection.rollback()

        print("[USER REGISTRATION ERROR]", error)

        return None

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================================
# GET USER BY EMAIL
# ==========================================================

def get_user_by_email(email):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return None

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, username, email, password_hash, role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        return cursor.fetchone()

    except Error as error:

        print("[USER LOGIN ERROR]", error)

        return None

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()