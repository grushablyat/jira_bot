from threading import Thread

from config import NOTIFY
from jira_bot import BOT
from notifier import app as notifier


if __name__ == '__main__':
    Thread(target=BOT.polling, kwargs={
        'non_stop': True
    }).start()

    Thread(target=notifier.run, kwargs={
        'host': NOTIFY['host'],
        'port': NOTIFY['port'],
    }).start()
