import telebot

from config import TG_TOKEN
from project.funcs import *
from service import user_repo, current_issue_repo, new_issue_repo
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
                if message.text == Button.LIST:
                    next_state = UserState.LIST
                    menu_list(BOT, chat.id)
                elif message.text == Button.NEW_ISSUE_PROJECT:
                    next_state = UserState.NEW_ISSUE_PROJECT
                    menu_new_issue_project(BOT, chat.id)
                else:
                    next_state = UserState.MENU
                    menu_existing(BOT, chat.id)

            case UserState.LIST:
                if message.text == Button.BACK:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                else:
                    next_state = UserState.LIST
                    menu_existing(BOT, chat.id)

                    # # is request to jira appropriate here?
                    # for issue in jira_imitation.get_issues():
                    #     if message.text == issue.title:
                    #         next_state = UserState.ISSUE
                    #         current_issue_repo.create(user.id, issue.id)
                    #         menu_issue(BOT, chat.id, issue)
                    #         break
                    # else:
                    #     next_state = UserState.LIST
                    #     menu_existing(BOT, chat.id)

            case UserState.ISSUE:
                if message.text == Button.STATUS:
                    next_state = UserState.STATUS
                    menu_status(BOT, chat.id)
                elif message.text == Button.BACK:
                    next_state = UserState.LIST
                    current_issue_repo.delete(user.id)
                    menu_list(BOT, chat.id)
                else:
                    next_state = UserState.ISSUE
                    menu_existing(BOT, chat.id)

            case UserState.STATUS:
                if [Button.TODO, Button.IN_PROGRESS, Button.DONE, Button.CANCEL].__contains__(message.text):
                    next_state = UserState.ISSUE
                    issue_id = current_issue_repo.get_by_user_id(user.id)

                    if message.text == Button.CANCEL:
                        issue = jira_imitation.get_issue_by_id(issue_id)
                    else:
                        issue = jira_imitation.update_issue_status(issue_id, message.text)

                    menu_issue(BOT, chat.id, issue)
                else:
                    next_state = UserState.STATUS
                    menu_existing(BOT, chat.id)

            case UserState.NEW_ISSUE_PROJECT:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_PROJECT
                    menu_existing(BOT, chat.id)

            case UserState.NEW_ISSUE_TITLE:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    new_issue_repo.update_title(user.id, message.text)
                    menu_new_issue_assignee(BOT, chat.id)

            case UserState.NEW_ISSUE_ASSIGNEE:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                elif message.text == Button.NO_ONE:
                    next_state = UserState.NEW_ISSUE_DESCRIPTION
                    menu_new_issue_description(BOT, chat.id)
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    menu_existing(BOT, chat.id)

            case UserState.NEW_ISSUE_DESCRIPTION:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_PREVIEW
                    new_issue_repo.update_description(user.id, message.text)
                    issue = new_issue_repo.get_by_user_id(user.id)
                    issue.status = Button.TODO
                    menu_new_issue_preview(BOT, chat.id, issue)

            case UserState.NEW_ISSUE_PREVIEW:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                elif message.text == Button.CREATE:
                    next_state = UserState.ISSUE
                    issue = new_issue_repo.get_by_user_id(user.id)
                    new_issue_repo.delete(user.id)
                    issue = jira_imitation.create_issue(issue)

                    current_issue_repo.create(user.id, issue.id)

                    menu_issue(BOT, chat.id, issue)

    except ValueError:
        BOT.send_message(chat.id, "WRONG STATE")
        print("WRONG STATE")

    user_repo.update(user.id, next_state)


@BOT.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat = call.message.chat
    user = call.from_user

    # Getting user's state
    result = user_repo.get_by_id(user.id)

    if result is None:
        print("NO SUCH USER")
        BOT.send_message(chat.id, "NO SUCH USER")
        return

    next_state = UserState.MENU

    try:
        match result.state:
            case UserState.LIST:
                # BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                #                       text='Список задач', reply_markup=None)
                BOT.delete_message(chat.id, call.message.message_id)

                # is request to jira appropriate here?
                for issue in jira_imitation.get_issues():
                    if call.data == issue.title:
                        next_state = UserState.ISSUE
                        current_issue_repo.create(user.id, issue.id)
                        menu_issue(BOT, chat.id, issue)
                        break
                else:
                    next_state = UserState.LIST
                    menu_existing(BOT, chat.id)

            case UserState.NEW_ISSUE_PROJECT:
                BOT.delete_message(chat.id, call.message.message_id)

                # is request to jira appropriate here?
                for project in jira_imitation.get_projects():
                    if call.data == project.title:
                        next_state = UserState.NEW_ISSUE_TITLE
                        new_issue_repo.create(user.id)
                        new_issue_repo.update_project(user.id, project.title)
                        menu_new_issue_title(BOT, chat.id)
                        break
                else:
                    next_state = UserState.NEW_ISSUE_PROJECT
                    menu_existing(BOT, chat.id)

            case UserState.NEW_ISSUE_ASSIGNEE:
                BOT.delete_message(chat.id, call.message.message_id)

                # is request to jira appropriate here?
                for assignee in jira_imitation.get_assignees():
                    if call.data == assignee.name:
                        next_state = UserState.NEW_ISSUE_DESCRIPTION
                        new_issue_repo.update_assignee(user.id, assignee.name)
                        menu_new_issue_description(BOT, chat.id)
                        break
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    menu_existing(BOT, chat.id)

    except ValueError:
        BOT.send_message(chat.id, "WRONG STATE")
        print("WRONG STATE")

    user_repo.update(user.id, next_state)


if __name__ == '__main__':
    BOT.polling(non_stop=True)
