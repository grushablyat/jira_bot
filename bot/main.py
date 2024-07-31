from threading import Thread

from jira_bot import BOT


if __name__ == '__main__':
    Thread(target=BOT.polling, kwargs={
        'non_stop': True
    }).start()
