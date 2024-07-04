from project.model.new_issue import NewIssue
from project.service import repo


def get_by_user_id(user_id):
    rs = repo.select(f'SELECT * FROM new_issue WHERE user_id={user_id}')

    issue = None
    if len(rs) == 1:
        issue = NewIssue(rs[0][0], rs[0][1], rs[0][2], rs[0][3], rs[0][4])

    return issue


def create(user_id):
    return repo.execute_query(f'INSERT INTO new_issue VALUES ({user_id})')


def delete(user_id):
    return repo.execute_query(f'DELETE FROM new_issue WHERE user_id={user_id}')


def update_project(user_id, project):
    return repo.execute_query(f"UPDATE new_issue SET project='{project}' WHERE user_id={user_id}")


def update_title(user_id, title):
    return repo.execute_query(f"UPDATE new_issue SET title='{title}' WHERE user_id={user_id}")


def update_assignee(user_id, assignee):
    return repo.execute_query(f"UPDATE new_issue SET assignee='{assignee}' WHERE user_id={user_id}")


def update_description(user_id, description):
    return repo.execute_query(f"UPDATE new_issue SET description='{description}' WHERE user_id={user_id}")
