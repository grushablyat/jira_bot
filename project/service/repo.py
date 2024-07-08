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
