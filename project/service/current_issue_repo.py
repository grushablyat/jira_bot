from psycopg2 import OperationalError, DatabaseError

from project.model.current_issue import CurrentIssue
from project.service import repo


def get_by_user_id(user_id):
    connection = repo.create_connection()

    if not connection:
        return None

    cursor = connection.cursor()
    result = None
    try:
        cursor.execute('''
            SELECT * FROM current_issue WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
        })
        result = cursor.fetchall()
    except OperationalError as e:
        repo.db_logger.error(e)
    finally:
        connection.close()

    issue = None

    if result is not None:
        if len(result) == 1:
            issue = CurrentIssue(result[0][1], result[0][2], result[0][3])

    return issue


def create(user_id):
    connection = repo.create_connection()

    if not connection:
        return None

    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO current_issue(user_id) VALUES(%(user_id)s)
        ''', {
            'user_id': user_id,
        })
        return True
    except DatabaseError as e:
        repo.db_logger.error(e)
        return False
    finally:
        connection.close()


def delete(user_id):
    connection = repo.create_connection()

    if not connection:
        return None

    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            DELETE FROM current_issue WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
        })
        return True
    except OperationalError as e:
        repo.db_logger.error(e)
        return False
    finally:
        connection.close()


def update(user_id, field, value):
    connection = repo.create_connection()

    if not connection:
        return None

    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(f'''
            UPDATE current_issue SET {field}= %(value)s WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
            'value': value,
        })
        return True
    except OperationalError as e:
        repo.db_logger.error(e)
        return False
    finally:
        connection.close()
