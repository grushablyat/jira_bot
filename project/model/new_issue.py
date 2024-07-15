class NewIssue:
    class Fields:
        def __init__(self, project, summary, assignee, description):
            self.project = project
            self.summary = summary
            self.status = 'To do'
            self.assignee = assignee
            self.description = description

    def __init__(self, user_id, project, summary, assignee, description):
        self.user_id = user_id
        self.project = project
        self.summary = summary
        self.assignee = assignee
        self.description = description

        self.fields = self.Fields(project, summary, assignee, description)

    def to_dict(self):
        return {
            'project': self.project,
            'summary': self.summary,
            'description': self.description,
            'issuetype': 'Задача'
        }
