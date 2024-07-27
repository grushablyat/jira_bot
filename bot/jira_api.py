import json
import logging

import requests
from jira import JIRA, JIRAError
from requests.auth import HTTPBasicAuth

from config import JIRA_PASSWORD, JIRA_URL, JIRA_USERNAME

jira_logger = logging.getLogger(__name__)

jira = JIRA(auth=(JIRA_USERNAME, JIRA_PASSWORD), options={'server': JIRA_URL})


def get_issues(assignee=None, project=None, status=None):
    issues = []

    try:
        jql_params = []

        if assignee:
            jql_params.append(f'assignee={assignee}')
        if project:
            jql_params.append(f'project={project}')

        issues_unfiltered = jira.search_issues('&'.join(jql_params))

        if status:
            for issue in issues_unfiltered:
                if issue.fields.status.name == status:
                    issues.append(issue)
        else:
            issues = issues_unfiltered

    except JIRAError as e:
        jira_logger.error(e)

    return issues


def get_issues_keys(assignee=None, project=None, status=None):
    keys = []

    for issue in get_issues(assignee, project, status):
        keys.append(issue.raw.get('key'))

    return keys


def get_projects_keys():
    keys = []
    projects = []

    try:
        projects = jira.projects()
    except JIRAError as e:
        jira_logger.error(e)

    if projects:
        for project in projects:
            keys.append(project.raw.get('key'))

    return keys


def get_possible_statuses(pkey):
    statuses = []

    try:
        if pkey:
            url = JIRA_URL + '/rest/api/2/project/' + pkey + '/statuses'
            auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_PASSWORD)

            headers = {
                "Accept": "application/json",
            }

            response = requests.request(
                "GET",
                url,
                headers=headers,
                auth=auth,
            )

            for status in json.loads(response.text)[0]['statuses']:
                statuses.append(status['name'])
        else:
            st = jira.statuses()
            for status in st:
                statuses.append(status.name)

    except JIRAError as e:
        jira_logger.error(e)

    return statuses


def get_issue_by_key(key):
    issue = None

    try:
        issue = jira.issue(key)
    except JIRAError as e:
        jira_logger.error(e)

    return issue


def get_possible_transitions(issue_key):
    transitions_names = []

    try:
        transitions = jira.transitions(issue_key)
        for transition in transitions:
            transitions_names.append(transition['name'])
    except JIRAError as e:
        jira_logger.error(e)

    return transitions_names


def update_issue_status(issue_key, transition):
    try:
        jira.transition_issue(issue_key, transition)
        return True
    except JIRAError as e:
        jira_logger.error(e)
        return False


def create_issue(issue_dict, assignee=None):
    new_issue = None

    try:
        new_issue = jira.create_issue(fields=issue_dict)
        if assignee:
            jira.assign_issue(new_issue.raw.get('key'), assignee)
    except JIRAError as e:
        jira_logger.error(e)

    return new_issue


def get_assignable_users(pkey):
    names = []

    try:
        users = jira.search_assignable_users_for_issues(project=pkey, query='.')
        for user in users:
            names.append(user.raw.get('name'))
    except JIRAError as e:
        jira_logger.error(e)

    return names


def get_possible_issue_types(pkey):
    issue_types = []

    try:
        it = jira.issue_types_for_project(pkey)
        for issue_type in it:
            issue_types.append(int(issue_type.raw.get('id')))
    except JIRAError | ValueError as e:
        jira_logger.error(e)

    return issue_types
