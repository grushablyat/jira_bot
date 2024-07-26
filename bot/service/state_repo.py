from psycopg2 import OperationalError, DatabaseError

from bot.service import repo


def get_by_user_id(user_id):
    connection = repo.create_connection()

    if not connection:
        return None

    cursor = connection.cursor()
    result = None
    try:
        cursor.execute('''
            SELECT * FROM state WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
        })
        result = cursor.fetchall()
    except OperationalError as e:
        repo.db_logger.error(e)
    finally:
        connection.close()

    state = None

    if result is not None:
        if len(result) == 1:
            state = result[0][1]

    return state


def create(user_id, state):
    connection = repo.create_connection()

    if not connection:
        return None

    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO state VALUES(%(user_id)s, %(state)s)
        ''', {
            'user_id': user_id,
            'state': state,
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
            DELETE FROM state WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
        })
        return True
    except OperationalError as e:
        repo.db_logger.error(e)
        return False
    finally:
        connection.close()


def update(user_id, new_state):
    connection = repo.create_connection()

    if not connection:
        return None

    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            UPDATE state SET state= %(state)s WHERE user_id=%(user_id)s
        ''', {
            'user_id': user_id,
            'state': new_state,
        })
        return True
    except OperationalError as e:
        repo.db_logger.error(e)
        return False
    finally:
        connection.close()
