next_id = 0


class Issue:
    def __init__(self, id, project, title, assignee, description, status):
        self.id = id
        self.project = project
        self.title = title
        self.assignee = assignee
        self.description = description
        self.status = status
        global next_id
        next_id += 1


issues = [
    Issue(0, 'project0', 'issue1', 'tip2', 'description1', 'Done'),
    Issue(1, 'project1', 'issue2', 'tip2', 'description2', 'In progress'),
    Issue(2, 'project0', 'issue3', 'tip1', 'description3', 'In progress'),
    Issue(3, 'project0', 'issue4', 'tip0', 'description4', 'To do'),
    Issue(4, 'project1', 'issue5', 'tip1', 'description5', 'To do'),
]


def get_issues():
    return issues


def get_issues_titles():
    titles = []
    for issue in issues:
        titles.append(issue.title)

    return titles


def get_issue_by_id(id):
    return issues[id]


def update_issue_status(id, status):
    issues[id].status = status
    return issues[id]


def create_issue(issue):
    issue = Issue(next_id, issue.project, issue.title, issue.assignee, issue.description, 'To do')
    issues.append(issue)
    return issue


class Project:
    def __init__(self, id, title):
        self.id = id
        self.title = title


projects = [
    Project(0, 'project0'),
    Project(1, 'project1'),
    # Project(2, 'project2'),
    # Project(3, 'project3'),
]


def get_projects():
    return projects


def get_projects_titles():
    titles = []
    for project in projects:
        titles.append(project.title)

    return titles


class Assignee:
    def __init__(self, id, name):
        self.id = id
        self.name = name


assignees = [
    Assignee(0, 'tip0'),
    Assignee(1, 'tip1'),
    Assignee(2, 'tip2'),
]


def get_assignees_names():
    names = []
    for assignee in assignees:
        names.append(assignee.name)

    return names


def get_assignees():
    return assignees
