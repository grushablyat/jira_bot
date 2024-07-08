from psycopg2 import OperationalError

from project.model.current_issue import CurrentIssue
from project.service import repo


def get_by_user_id(user_id):
    connection = repo.create_connection()
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute('''
            SELECT * FROM current_issue WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
        })
        result = cursor.fetchall()
    except OperationalError:
        pass
    finally:
        connection.close()

    issue_id = None

    if result is not None:
        if len(result) == 1:
            issue_id = result[0][1]

    return issue_id


def create(user_id, issue_id):
    connection = repo.create_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO current_issue VALUES(%(user_id)s, %(issue_id)s)
        ''', {
            'user_id': user_id,
            'issue_id': issue_id,
        })
        return True
    except OperationalError:
        return False
    finally:
        connection.close()


def delete(user_id):
    connection = repo.create_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            DELETE FROM current_issue WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
        })
        return True
    except OperationalError:
        return False
    finally:
        connection.close()
