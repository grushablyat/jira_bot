from psycopg2 import OperationalError

from bot.model.user import User
from bot.service import repo


def get_by_id(user_id):
    connection = repo.create_connection()

    if not connection:
        return None

    cursor = connection.cursor()
    result = None
    try:
        cursor.execute('''
            SELECT * FROM users WHERE id=%(id)s
        ''', {
            'id': user_id,
        })
        result = cursor.fetchall()
    except OperationalError as e:
        repo.db_logger.error(e)
    finally:
        connection.close()

    user = None

    if result is not None:
        if len(result) == 1:
            user = User(result[0][0], result[0][1], result[0][2])

    return user


def get_by_jira_username(jira_username):
    connection = repo.create_connection()

    if not connection:
        return None

    cursor = connection.cursor()
    result = None

    try:
        cursor.execute('''
            SELECT * FROM users WHERE jira_username=%(jira_username)s
        ''', {
            'jira_username': jira_username,
        })
        result = cursor.fetchall()
    except OperationalError as e:
        repo.db_logger.error(e)
    finally:
        connection.close()

    user = None

    if result:
        user = User(result[0][0], result[0][1], result[0][2])

    return user
