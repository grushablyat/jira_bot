from jira import JIRA, JIRAError

from project.config import JIRA_URL, JIRA_USERNAME, JIRA_PASSWORD


jira = JIRA(auth=(JIRA_USERNAME, JIRA_PASSWORD), options={'server': JIRA_URL})


def get_issues(assignee=None):
    issues = []

    try:
        issues = jira.search_issues('' if not assignee else f'assignee={assignee}')
    except JIRAError as e:
        print('get_issues() error:')
        print(e, end='\n\n')

    return issues


def get_issues_keys(assignee=None):
    keys = []
    for issue in get_issues(assignee):
        keys.append(issue.raw.get('key'))

    return keys


def get_issue_by_key(key):
    issue = None

    try:
        issue = jira.issue(key)
    except JIRAError as e:
        print('get_issue_by_key(...) error:')
        print(e, end='\n\n')

    return issue


def update_issue_status(issue_key, transition):
    try:
        jira.transition_issue(issue_key, transition)
        return True
    except JIRAError as e:
        print('update_issue_status(...) error:')
        print(e, end='\n\n')
        return False


def create_issue(issue_dict, assignee=None):
    new_issue = None

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        if assignee:
            jira.assign_issue(new_issue.raw.get('key'), assignee)
    except JIRAError as e:
        print('create_issue(...) error:')
        print(e, end='\n\n')

    return new_issue


def get_projects_keys():
    keys = []
    projects = []

    try:
        projects = jira.projects()
    except JIRAError as e:
        print('get_projects_keys() error:')
        print(e, end='\n\n')

    for project in projects:
        keys.append(project.raw.get('key'))

    return keys


def get_assignees_names():
    names = []

    try:
        for assignee in jira.search_users('.'):
            names.append(assignee.name)
    except JIRAError as e:
        print('get_assignees_names() error:')
        print(e, end='\n\n')

    return names
