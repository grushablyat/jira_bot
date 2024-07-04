from psycopg2 import connect, OperationalError

from project.config import DBC


def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        # print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        pass
        # print(f"The error '{e}' occurred")

    return connection


def select(query):
    connection = create_connection(DBC['database'], DBC['username'], DBC['password'], DBC['host'], DBC['port'])
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except OperationalError as e:
        pass
        # print(f"The error '{e}' occurred")

    connection.close()
    return result


def execute_query(query):
    connection = create_connection(DBC['database'], DBC['username'], DBC['password'], DBC['host'], DBC['port'])
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # print("Query executed successfully")
        return True
    except OperationalError as e:
        # print(f"The error '{e}' occurred")
        return False
    finally:
        connection.close()
