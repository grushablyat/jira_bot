from project.model.user import User
from project.service import repo


def get_all():
    rs = repo.select(f'SELECT * FROM users')

    users = []
    for row in rs:
        users.append(User(row['id'], row['state']))

    return users


def get_by_id(id):
    rs = repo.select(f'SELECT * FROM users WHERE id={id}')

    user = None
    if len(rs) == 1:
        user = User(rs[0][0], rs[0][1])

    return user


def create(user):
    return repo.execute_query(f'INSERT INTO users (id, state) VALUES ({user.id}, {user.state})')


def delete(id):
    repo.execute_query(f'DELETE FROM current_issue WHERE user_id={id}')
    repo.execute_query(f'DELETE FROM new_issue WHERE user_id={id}')
    return repo.execute_query(f'DELETE FROM users WHERE id={id}')


def update(id, new_state):
    return repo.execute_query(f'UPDATE users SET state={new_state} WHERE id={id}')
