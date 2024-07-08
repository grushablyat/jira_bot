from psycopg2 import connect, OperationalError

from project.config import DBC


def create_connection():
    connection = None
    try:
        connection = connect(
            database=DBC['database'],
            user=DBC['username'],
            password=DBC['password'],
            host=DBC['host'],
            port=DBC['port'],
        )
    except OperationalError:
        pass

    return connection


def select(query):
    connection = create_connection()
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except OperationalError:
        pass

    connection.close()
    return result


def execute_query(query):
    connection = create_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        return True
    except OperationalError:
        return False
    finally:
        connection.close()
