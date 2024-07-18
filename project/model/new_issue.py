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
        return {
            'project': self.project,
            'summary': self.summary,
            'description': self.description,
            'issuetype': 10004
        }
