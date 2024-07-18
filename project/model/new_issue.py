from project.testim_jira_api import get_possible_issue_types


class NewIssue:
    class Fields:
        def __init__(self, project, summary, assignee, description):
            self.project = project
            self.summary = summary
            self.status = None
            self.assignee = assignee
            self.description = description

    def __init__(self, user_id, project, summary, assignee, description):
        self.key = project + '-X'
        self.user_id = user_id
        self.project = project
        self.summary = summary
        self.assignee = assignee
        self.description = description

        self.fields = self.Fields(project, summary, assignee, description)

    def to_dict(self):
        try:
            types = get_possible_issue_types(self.project)
            return None if not types or len(types) == 0 else {
                'project': self.project,
                'summary': self.summary,
                'description': self.description,
                'issuetype': 10004 if '10004' in types else 10000 if '10000' in types else int(types[0]),
            }
        except ValueError:
            return None
