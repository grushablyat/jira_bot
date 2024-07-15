from psycopg2 import OperationalError

from project.model.user import User
from project.service import repo


def get_by_id(user_id):
    connection = repo.create_connection()
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute('''
            SELECT * FROM users WHERE id=%(id)s
        ''', {
            'id': user_id,
        })
        result = cursor.fetchall()
    except OperationalError:
        pass
    finally:
        connection.close()

    user = None

    if result is not None:
        if len(result) == 1:
            user = User(result[0][0], result[0][1], result[0][2])

    return user
