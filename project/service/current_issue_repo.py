from psycopg2 import OperationalError, DatabaseError

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

    issue_key = None

    if result is not None:
        if len(result) == 1:
            issue_key = CurrentIssue(result[0][1], result[0][2], result[0][3])

    return issue_key


def create(user_id):
    connection = repo.create_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO current_issue(user_id) VALUES(%(user_id)s)
        ''', {
            'user_id': user_id,
        })
        return True
    except DatabaseError:
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


def update(user_id, field, value):
    connection = repo.create_connection()
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
    except OperationalError:
        return False
    finally:
        connection.close()
