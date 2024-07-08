from psycopg2 import OperationalError

from project.service import repo, current_issue_repo, new_issue_repo


def get_state_by_id(id):
    connection = repo.create_connection()
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute('''
            SELECT * FROM users WHERE id=%(id)s
        ''', {
            'id': id,
        })
        result = cursor.fetchall()
    except OperationalError:
        pass
    finally:
        connection.close()

    state = None
    if result is not None:
        if len(result) == 1:
            state = result[0][1]

    return state


def create(id, state):
    connection = repo.create_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO users VALUES(%(id)s, %(state)s)
        ''', {
            'id': id,
            'state': state,
        })
        return True
    except OperationalError:
        return False
    finally:
        connection.close()


def delete(id):
    current_issue_repo.delete(id)
    new_issue_repo.delete(id)

    connection = repo.create_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
            DELETE FROM users WHERE id=%(id)s
        ''', {
            'id': id,
        })
        return True
    except OperationalError:
        return False
    finally:
        connection.close()


def update(id, new_state):
    connection = repo.create_connection()
    connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute('''
                UPDATE users SET state= %(state)s WHERE id=%(id)s
            ''', {
            'id': id,
            'state': new_state,
        })
        return True
    except OperationalError:
        return False
    finally:
        connection.close()
