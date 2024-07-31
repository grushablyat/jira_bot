from flask import Flask, request

from bot.service import user_repo
from jira_api import get_issue_by_key
from jira_bot import BOT


app = Flask(__name__)


@app.route('/transition_made', methods=['POST'])
def issue_updated():
    # issue = {
    #     'ikey': request.args.get('ikey'),
    #     'status': request.args.get('status'),
    #     'reporter': request.args.get('reporter'),
    # }
    #
    # reporter = user_repo.get_by_jira_username(issue['reporter'])
    #
    # if reporter:
    #     BOT.send_message(reporter.id, f'У задачи {issue['ikey']} изменился статус!\nНовый статус: {issue['status']}')

    ikey = request.args.get('ikey')

    issue = get_issue_by_key(ikey)

    reporter = user_repo.get_by_jira_username(issue.fields.reporter.name)

    if reporter:
        BOT.send_message(reporter.id, f'У задачи {ikey} изменился статус!\nНовый статус: {issue.fields.status.name}')

    return ''
