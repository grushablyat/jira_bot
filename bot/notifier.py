from time import sleep
from threading import Thread

from flask import Flask, request

from bot.service import user_repo
from jira_api import get_issue_by_key
from jira_bot import BOT, create_inline_markup

app = Flask(__name__)


@app.route('/transition_made', methods=['POST'])
def transition_made():
    # issue = {
    #     'ikey': request.args.get('ikey'),
    #     'status': request.args.get('status'),
    #     # 'reporter': request.args.get('reporter'),
    # }
    #
    # reporter = user_repo.get_by_jira_username(issue['reporter'])
    #
    # if reporter:
    #     BOT.send_message(reporter.id, f'У задачи {issue['ikey']} изменился статус!\nНовый статус: {issue['status']}')

    ikey = request.args.get('ikey')
    # status = request.args.get('status')

    issue = get_issue_by_key(ikey)
    if issue:
        reporter = user_repo.get_by_jira_username(issue.fields.reporter.name)

        if reporter:
            BOT.send_message(reporter.id, f'У задачи {ikey} изменился статус!')
            # BOT.send_message(reporter.id, f'У задачи {ikey} изменился статус!\n'
            #                               f'Новый статус: {status}')

    # ikey = request.args.get('ikey')
    #
    # issue = get_issue_by_key(ikey)
    # if issue:
    #     reporter = user_repo.get_by_jira_username(issue.fields.reporter.name)
    #
    #     if reporter:
    #         BOT.send_message(reporter.id, f'У задачи {ikey} изменился статус!\n',
    #                          reply_keyboard=create_inline_markup(default=('Просмотреть ' + ikey)))

    # ikey = request.args.get('ikey')
    #
    # Thread(target=notify, kwargs={
    #     'ikey': ikey
    # }).start()

    return ''


# def notify(ikey):
#     sleep(1)
#     issue = get_issue_by_key(ikey)
#     if issue:
#         reporter = user_repo.get_by_jira_username(issue.fields.reporter.name)
#
#         if reporter:
#             BOT.send_message(reporter.id, f'У задачи {ikey} изменился статус!\n'
#                                           f'Новый статус: {issue.fields.status.name}')
