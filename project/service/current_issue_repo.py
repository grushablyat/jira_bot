from project.model.current_issue import CurrentIssue
from project.service import repo


def get_by_user_id(user_id):
    rs = repo.select(f'SELECT * FROM current_issue WHERE user_id={user_id}')

    issue_id = None
    if len(rs) == 1:
        issue_id = rs[0][1]

    return issue_id


def create(user_id, issue_id):
    return repo.execute_query(f'INSERT INTO current_issue VALUES ({user_id}, {issue_id})')


def delete(user_id):
    return repo.execute_query(f'DELETE FROM current_issue WHERE user_id={user_id}')
