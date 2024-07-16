from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import testim_jira_api
from button import Button, STATUS_MENU
from config import TG_TOKEN
from service import user_repo, state_repo, current_issue_repo, new_issue_repo
from states import UserState

BOT = TeleBot(token=TG_TOKEN)


def create_markup(*args):
    actions = []
    for arg in args:
        actions.append(KeyboardButton(arg))

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*actions)

    return markup


def create_inline_markup(*args):
    actions = []
    for arg in args:
        actions.append(InlineKeyboardButton(arg, callback_data=arg))

    markup = InlineKeyboardMarkup()
    markup.add(*actions)

    return markup


def format_issue(issue):
    return (f'<b><i>Задача</i></b>:\n{issue.key}\n\n'
            f'<b><i>Название</i></b>:\n{issue.fields.summary}\n\n'
            f'<b><i>Исполнитель</i></b>:\n{issue.fields.assignee if issue.fields.assignee else 'Нет'}\n\n'
            f'<b><i>Статус</i></b>:\n{issue.fields.status}\n\n'
            f'<b><i>Описание</i></b>:\n{issue.fields.description}')


def menu_existing(chat_id, text=None, inline_markup=None):
    BOT.send_message(chat_id, text if text else 'Выберите существующее действие', reply_markup=inline_markup)


def menu_menu(chat_id):
    BOT.send_message(chat_id, 'Выберите нужное действие',
                     reply_markup=create_markup(Button.LIST, Button.NEW_ISSUE_PROJECT))


def menu_list(chat_id, user_id):
    assignee = user_repo.get_by_id(user_id)

    if assignee.admin:
        assignee = None
    else:
        assignee = assignee.jira_username

    BOT.send_message(chat_id, 'Выберите задачу', reply_markup=create_markup(Button.BACK))
    BOT.send_message(chat_id, 'Список задач:',
                     reply_markup=create_inline_markup(*testim_jira_api.get_issues_keys(assignee)))


def menu_issue(chat_id, issue):
    BOT.send_message(chat_id, format_issue(issue), parse_mode='HTML',
                     reply_markup=create_markup(Button.STATUS, Button.BACK))


def menu_new_issue_project(chat_id):
    BOT.send_message(chat_id, 'Список проектов:',
                     reply_markup=create_inline_markup(*testim_jira_api.get_projects_keys()))


def menu_new_issue_assignee(chat_id):
    BOT.send_message(chat_id, 'Список исполнителей:',
                     reply_markup=create_inline_markup(*testim_jira_api.get_assignees_names()))


@BOT.message_handler(commands=['start'])
def start(message):
    chat = message.chat
    user = message.from_user

    BOT.send_message(chat.id, f'Добро пожаловать, {user.first_name}!')

    current_issue_repo.delete(user.id)
    new_issue_repo.delete(user.id)
    state_repo.delete(user.id)
    state_repo.create(user.id, UserState.MENU)

    menu_menu(chat.id)


@BOT.message_handler(content_types=['text'])
def text_handler(message):
    chat = message.chat
    user = message.from_user

    current_state = state_repo.get_state_by_id(user.id)

    if current_state is None:
        BOT.send_message(chat.id, "Пользователь не зарегистрирован, нажмите /start")
        return

    next_state = UserState.MENU

    try:
        match current_state:
            case UserState.MENU:
                if message.text == Button.LIST:
                    next_state = UserState.LIST
                    menu_list(chat.id, user.id)
                elif message.text == Button.NEW_ISSUE_PROJECT:
                    if user_repo.get_by_id(user.id).admin:
                        next_state = UserState.NEW_ISSUE_PROJECT
                        BOT.send_message(chat.id, 'Выберите проект', reply_markup=create_markup(Button.CANCEL))
                        menu_new_issue_project(chat.id)
                    else:
                        next_state = UserState.MENU
                        BOT.send_message(chat.id, 'Функция создания задачи доступна только администраторам')
                else:
                    next_state = UserState.MENU
                    menu_existing(chat.id)

            case UserState.LIST:
                BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                      text=f'Список задач', reply_markup=None)
                if message.text == Button.BACK:
                    next_state = UserState.MENU
                    menu_menu(chat.id)
                else:
                    next_state = UserState.LIST

                    BOT.send_message(chat.id, 'Выберите существующую задачу')
                    menu_list(chat.id, user.id)

            case UserState.ISSUE:
                if message.text == Button.STATUS:
                    next_state = UserState.STATUS
                    BOT.send_message(chat.id, 'Выберите новый статус задачи',
                                     reply_markup=create_markup(*STATUS_MENU))
                elif message.text == Button.BACK:
                    next_state = UserState.LIST
                    current_issue_repo.delete(user.id)
                    menu_list(chat.id, user.id)
                else:
                    next_state = UserState.ISSUE
                    menu_existing(chat.id)

            case UserState.STATUS:
                if message.text in STATUS_MENU:
                    next_state = UserState.ISSUE
                    issue_key = current_issue_repo.get_by_user_id(user.id)

                    if issue_key is not None:
                        if message.text != Button.CANCEL:
                            testim_jira_api.update_issue_status(issue_key, message.text)
                        issue = testim_jira_api.get_issue_by_key(issue_key)

                        menu_issue(chat.id, issue)
                    else:
                        next_state = UserState.LIST
                        current_issue_repo.delete(user.id)
                        menu_existing(chat.id, "Произошла ошибка, попробуйте снова")
                        menu_list(chat.id, user.id)
                else:
                    next_state = UserState.STATUS
                    menu_existing(chat.id)

            case UserState.NEW_ISSUE_PROJECT:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                          text=f'Список проектов', reply_markup=None)
                    menu_menu(chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_PROJECT
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                          text=f'Список проектов', reply_markup=None)
                    BOT.send_message(chat.id, 'Выберите существующий проект')
                    menu_new_issue_project(chat.id)

            case UserState.NEW_ISSUE_SUMMARY:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    new_issue_repo.update(user.id, 'summary', message.text)
                    BOT.send_message(chat.id, 'Выберите исполнителя',
                                     reply_markup=create_markup(Button.NO_ONE, Button.CANCEL))
                    menu_new_issue_assignee(chat.id)

            case UserState.NEW_ISSUE_ASSIGNEE:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                          text=f'Список исполнителей', reply_markup=None)
                    menu_menu(chat.id)
                    new_issue_repo.delete(user.id)
                elif message.text == Button.NO_ONE:
                    next_state = UserState.NEW_ISSUE_DESCRIPTION
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                          text=f'Без исполнителя', reply_markup=None)
                    BOT.send_message(chat.id, 'Введите описание задачи',
                                     reply_markup=create_markup(Button.CANCEL))
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                          text=f'Список исполнителей', reply_markup=None)
                    BOT.send_message(chat.id, 'Выберите существующего исполнителя')
                    menu_new_issue_assignee(chat.id)

            case UserState.NEW_ISSUE_DESCRIPTION:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_PREVIEW
                    new_issue_repo.update(user.id, 'description', message.text)
                    issue = new_issue_repo.get_by_user_id(user.id)
                    if issue is not None:
                        issue.status = Button.TODO
                        BOT.send_message(chat.id, format_issue(issue), parse_mode='HTML')
                        BOT.send_message(chat.id, 'Подтвердите создание задачи',
                                         reply_markup=create_markup(Button.CREATE, Button.CANCEL))
                    else:
                        next_state = UserState.MENU
                        new_issue_repo.delete(user.id)
                        menu_existing(chat.id, 'Произошла ошибка, попробуйте снова')
                        menu_menu(chat.id)

            case UserState.NEW_ISSUE_PREVIEW:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(chat.id)
                    new_issue_repo.delete(user.id)
                elif message.text == Button.CREATE:
                    next_state = UserState.ISSUE
                    issue = new_issue_repo.get_by_user_id(user.id)
                    new_issue_repo.delete(user.id)
                    if issue is not None:
                        issue = testim_jira_api.create_issue(issue.to_dict(), issue.assignee)
                        current_issue_repo.create(user.id, issue.raw.get('key'))
                        menu_issue(chat.id, issue)
                    else:
                        next_state = UserState.MENU
                        menu_existing(chat.id, 'Произошла ошибка, попробуйте снова')
                        menu_menu(chat.id)

            case _:
                BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    except ValueError:
        BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    state_repo.update(user.id, next_state)


@BOT.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat = call.message.chat
    user = call.from_user

    current_state = state_repo.get_state_by_id(user.id)

    if current_state is None:
        BOT.send_message(chat.id, "Пользователь не зарегистрирован, нажмите /start")
        return

    next_state = UserState.MENU

    try:
        match current_state:
            case UserState.LIST:
                for issue in testim_jira_api.get_issues():
                    if call.data == issue.raw.get('key'):
                        next_state = UserState.ISSUE
                        current_issue_repo.create(user.id, issue.raw.get('key'))
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Список задач', reply_markup=None)
                        menu_issue(chat.id, issue)
                        break
                else:
                    next_state = UserState.LIST
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такой задачи', reply_markup=None)
                    menu_existing(chat.id)

            case UserState.NEW_ISSUE_PROJECT:
                for pkey in testim_jira_api.get_projects_keys():
                    if call.data == pkey:
                        next_state = UserState.NEW_ISSUE_SUMMARY
                        new_issue_repo.create(user.id)
                        new_issue_repo.update(user.id, 'project', pkey)
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Проект: <b>{pkey}</b>', reply_markup=None,
                                              parse_mode='HTML')
                        BOT.send_message(chat.id, 'Введите название задачи:',
                                         reply_markup=create_markup(Button.CANCEL))
                        break
                else:
                    next_state = UserState.NEW_ISSUE_PROJECT
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такого проекта', reply_markup=None)
                    menu_existing(chat.id)

            case UserState.NEW_ISSUE_ASSIGNEE:
                for assignee in testim_jira_api.get_assignees_names():
                    if call.data == assignee:
                        next_state = UserState.NEW_ISSUE_DESCRIPTION
                        new_issue_repo.update(user.id, 'assignee', assignee)
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Исполнитель: <b>{assignee}</b>', reply_markup=None,
                                              parse_mode='HTML')
                        BOT.send_message(chat.id, 'Введите описание задачи',
                                         reply_markup=create_markup(Button.CANCEL))
                        break
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такого исполнителя', reply_markup=None)
                    menu_existing(chat.id)

            case UserState.MENU | UserState.ISSUE | UserState.STATUS | UserState.NEW_ISSUE_SUMMARY | \
                 UserState.NEW_ISSUE_DESCRIPTION | UserState.NEW_ISSUE_PREVIEW:
                pass

            case _:
                BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    except ValueError:
        BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    state_repo.update(user.id, next_state)


if __name__ == '__main__':
    BOT.polling(non_stop=True)
