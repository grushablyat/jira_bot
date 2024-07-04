class Issue:
    def __init__(self, id, project, title, assignee, description, status):
        self.id = id
        self.project = project
        self.title = title
        self.assignee = assignee
        self.description = description
        self.status = status


issues = [
    Issue(0, 'project0', 'issue1', 'tip2', 'description1', 'Done'),
    Issue(1, 'project1', 'issue2', 'tip2', 'description2', 'In progress'),
    Issue(2, 'project0', 'issue3', 'tip1', 'description3', 'In progress'),
    Issue(3, 'project0', 'issue4', 'tip3', 'description4', 'To do'),
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


class Project:
    def __init__(self, id, name):
        self.id = id
        self.name = name


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
        titles.append(project.name)

    return titles
