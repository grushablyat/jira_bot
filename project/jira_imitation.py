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
    Issue(0, 'Проект 0', 'Задача 1', 'Исполнитель 2', 'Описание 1', 'Done'),
    Issue(1, 'Проект 1', 'Задача 2', 'Исполнитель 2', 'Описание 2', 'In progress'),
    Issue(2, 'Проект 0', 'Задача 3', 'Исполнитель 1', 'Описание 3', 'In progress'),
    Issue(3, 'Проект 0', 'Задача 4', 'Исполнитель 0', 'Описание 4', 'To do'),
    Issue(4, 'Проект 1', 'Задача 5', 'Исполнитель 1', 'Описание 5', 'To do'),
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
    Project(0, 'Проект 0'),
    Project(1, 'Проект 1'),
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
    Assignee(0, 'Исполнитель 0'),
    Assignee(1, 'Исполнитель 1'),
    Assignee(2, 'Исполнитель 2'),
]


def get_assignees_names():
    names = []
    for assignee in assignees:
        names.append(assignee.name)

    return names


def get_assignees():
    return assignees
