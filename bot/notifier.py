from threading import Thread

from flask import Flask, request

from bot.service import user_repo
from config import NOTIFY
from jira_bot import BOT


app = Flask(__name__)


@app.route('/issue_updated', methods=['POST'])
def issue_updated():
    issue = {
        'ikey': request.args.get('ikey'),
        'status': request.args.get('status'),
        'reporter': request.args.get('reporter'),
    }

    reporter = user_repo.get_by_jira_username(issue['reporter'])

    if reporter:
        BOT.send_message(reporter.id, f'У задачи {issue['ikey']} изменился статус!\nНовый статус: {issue['status']}')

    return ''


def run():
    Thread(target=app.run, kwargs={
        'host': NOTIFY['host'],
        'port': NOTIFY['port'],
    }).start()


if __name__ == '__main__':
    app.run(host=NOTIFY['host'], port=NOTIFY['port'], debug=True)
