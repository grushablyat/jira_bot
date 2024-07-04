from project.model.current_issue import CurrentIssue
from project.service import repo


def get_by_user_id(connection, user_id):
    rs = repo.select(connection, f'SELECT * FROM current_issue WHERE user_id={user_id}')

    issue_id = None
    if len(rs) == 1:
        issue_id = rs[0][1]

    return issue_id


def create(connection, user_id, issue_id):
    return repo.execute_query(connection, f'INSERT INTO current_issue VALUES ({user_id}, {issue_id})')


def delete(connection, user_id):
    return repo.execute_query(connection, f'DELETE FROM current_issue WHERE user_id={user_id}')
