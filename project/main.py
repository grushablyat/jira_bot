import telebot

from config import TG_TOKEN
from project.funcs import *
from service import user_repo, current_issue_repo
from states import UserState
from model.user import User


BOT = telebot.TeleBot(token=TG_TOKEN)


@BOT.message_handler(commands=['start'])
def start(message):
    chat = message.chat
    user = message.from_user

    BOT.send_message(chat.id, f'Добро пожаловать, {user.first_name}!')

    user_repo.delete(user.id)
    user_repo.create(User(user.id, UserState.MENU))

    menu_menu(BOT, chat.id)


@BOT.message_handler(content_types=['text'])
def text_handler(message):
    chat = message.chat
    user = message.from_user

    # Getting user's state
    result = user_repo.get_by_id(user.id)

    if result is None:
        print("NO SUCH USER")
        BOT.send_message(chat.id, "NO SUCH USER")
        return

    next_state = UserState.MENU

    try:
        match result.state:
            case UserState.MENU:
                if message.text == 'Просмотреть список задач':
                    next_state = UserState.LIST
                    menu_list(BOT, chat.id)
                elif message.text == 'Создать задачу':
                    next_state = UserState.NEW_ISSUE_PROJECT
                    menu_new_issue_project(BOT, chat.id)
                else:
                    next_state = UserState.MENU
                    menu_existing(BOT, chat.id)

            case UserState.LIST:
                if message.text == 'Назад':
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                else:
                    response_is_valid = False
                    for issue in jira_imitation.get_issues():
                        if message.text == issue.title:
                            next_state = UserState.ISSUE
                            current_issue_repo.create(user.id, issue.id)
                            menu_issue(BOT, chat.id, issue)
                            response_is_valid = True
                            break
                    if not response_is_valid:
                        next_state = UserState.LIST
                        menu_existing(BOT, chat.id)

            case UserState.ISSUE:
                if message.text == 'Изменить статус задачи':
                    next_state = UserState.STATUS
                    menu_status(BOT, chat.id)
                elif message.text == 'Назад':
                    next_state = UserState.LIST
                    current_issue_repo.delete(user.id)
                    menu_list(BOT, chat.id)
                else:
                    next_state = UserState.ISSUE
                    menu_existing(BOT, chat.id)
            case UserState.STATUS:
                if ['To do', 'In progress', 'Done', 'Отмена'].__contains__(message.text):
                    next_state = UserState.ISSUE
                    issue_id = current_issue_repo.get_by_user_id(user.id)

                    if message.text == 'Отмена':
                        issue = jira_imitation.get_issue_by_id(issue_id)
                    else:
                        issue = jira_imitation.update_issue_status(issue_id, message.text)

                    menu_issue(BOT, chat.id, issue)
                else:
                    next_state = UserState.STATUS
                    menu_existing(BOT, chat.id)

    except ValueError:
        BOT.send_message(chat.id, "WRONG STATE")
        print("WRONG STATE")

    user_repo.update(user.id, next_state)


if __name__ == '__main__':
    BOT.polling(non_stop=True)
