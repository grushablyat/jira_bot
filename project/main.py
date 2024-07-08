from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import jira_imitation
from config import TG_TOKEN
from model.user import User
from project.button import Button, STATUS_MENU
from service import user_repo, current_issue_repo, new_issue_repo
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
    return f'<b>{issue.title}</b> ({issue.status})\n{issue.assignee}\n\n{issue.description}'


def menu_existing(bot, chat_id, text=None, inline_markup=None):
    bot.send_message(chat_id, text if text else 'Выберите существующее действие', reply_markup=inline_markup)


def menu_menu(bot, chat_id):
    bot.send_message(chat_id, 'Выберите нужное действие',
                     reply_markup=create_markup(Button.LIST, Button.NEW_ISSUE_PROJECT))


def menu_list(bot, chat_id):
    bot.send_message(chat_id, 'Выберите задачу', reply_markup=create_markup(Button.BACK))
    bot.send_message(chat_id, 'Список задач', reply_markup=create_inline_markup(*jira_imitation.get_issues_titles()))


def menu_issue(bot, chat_id, issue):
    bot.send_message(chat_id, format_issue(issue), parse_mode='HTML',
                     reply_markup=create_markup(Button.STATUS, Button.BACK))


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
        BOT.send_message(chat.id, "Пользователь не зарегистрирован, нажмите /start")
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
                    BOT.send_message(chat.id, 'Выберите проект', reply_markup=create_markup(Button.CANCEL))
                    BOT.send_message(chat.id, 'Список проектов',
                                     reply_markup=create_inline_markup(*jira_imitation.get_projects_titles()))
                else:
                    next_state = UserState.MENU
                    menu_existing(BOT, chat.id)

            case UserState.LIST:
                if message.text == Button.BACK:
                    next_state = UserState.MENU
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id-1,
                                          text=f'Список задач', reply_markup=None)
                    menu_menu(BOT, chat.id)
                else:
                    next_state = UserState.LIST
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id-1,
                                          text=f'Список задач', reply_markup=None)
                    menu_existing(BOT, chat.id, 'Выберите существующую\nзадачу',
                                  create_inline_markup(*jira_imitation.get_issues_titles()))

            case UserState.ISSUE:
                if message.text == Button.STATUS:
                    next_state = UserState.STATUS
                    BOT.send_message(chat.id, 'Выберите новый статус задачи',
                                     reply_markup=create_markup(Button.TODO, Button.IN_PROGRESS,
                                                                Button.DONE, Button.CANCEL))
                elif message.text == Button.BACK:
                    next_state = UserState.LIST
                    current_issue_repo.delete(user.id)
                    menu_list(BOT, chat.id)
                else:
                    next_state = UserState.ISSUE
                    menu_existing(BOT, chat.id)

            case UserState.STATUS:
                if message.text in STATUS_MENU:
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
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id-1,
                                          text=f'Список проектов', reply_markup=None)
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_PROJECT
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id-1,
                                          text=f'Список проектов', reply_markup=None)
                    menu_existing(BOT, chat.id, 'Выберите существующий\nпроект',
                                  create_inline_markup(*jira_imitation.get_projects_titles()))

            case UserState.NEW_ISSUE_TITLE:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    new_issue_repo.update(user.id, 'title', message.text)
                    BOT.send_message(chat.id, 'Выберите исполнителя',
                                     reply_markup=create_markup(Button.NO_ONE, Button.CANCEL))
                    BOT.send_message(chat.id, 'Список исполнителей',
                                     reply_markup=create_inline_markup(*jira_imitation.get_assignees_names()))

            case UserState.NEW_ISSUE_ASSIGNEE:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id-1,
                                          text=f'Список исполнителей', reply_markup=None)
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                elif message.text == Button.NO_ONE:
                    next_state = UserState.NEW_ISSUE_DESCRIPTION
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id-1,
                                          text=f'Без исполнителя', reply_markup=None)
                    BOT.send_message(chat.id, 'Введите описание задачи',
                                     reply_markup=create_markup(Button.CANCEL))
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id-1,
                                          text=f'Список исполнителей', reply_markup=None)
                    menu_existing(BOT, chat.id, 'Выберите существующего\nисполнителя',
                                  create_inline_markup(*jira_imitation.get_assignees_names()))

            case UserState.NEW_ISSUE_DESCRIPTION:
                if message.text == Button.CANCEL:
                    next_state = UserState.MENU
                    menu_menu(BOT, chat.id)
                    new_issue_repo.delete(user.id)
                else:
                    next_state = UserState.NEW_ISSUE_PREVIEW
                    new_issue_repo.update(user.id, 'description', message.text)
                    issue = new_issue_repo.get_by_user_id(user.id)
                    issue.status = Button.TODO
                    BOT.send_message(chat.id, format_issue(issue), parse_mode='HTML')
                    BOT.send_message(chat.id, 'Подтвердите создание задачи',
                                     reply_markup=create_markup(Button.CREATE, Button.CANCEL))

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

            case _:
                BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    except ValueError:
        BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    user_repo.update(user.id, next_state)


@BOT.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat = call.message.chat
    user = call.from_user

    # Getting user's state
    result = user_repo.get_by_id(user.id)

    if result is None:
        BOT.send_message(chat.id, "Пользователь не зарегистрирован, нажмите /start")
        return

    next_state = UserState.MENU

    try:
        match result.state:
            case UserState.LIST:
                # is request to jira appropriate here?
                for issue in jira_imitation.get_issues():
                    if call.data == issue.title:
                        next_state = UserState.ISSUE
                        current_issue_repo.create(user.id, issue.id)
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Задача: <b>{issue.title}</b>', reply_markup=None,
                                              parse_mode='HTML')
                        menu_issue(BOT, chat.id, issue)
                        break
                else:
                    next_state = UserState.LIST
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такой задачи', reply_markup=None)
                    menu_existing(BOT, chat.id)

            case UserState.NEW_ISSUE_PROJECT:
                # is request to jira appropriate here?
                for project in jira_imitation.get_projects():
                    if call.data == project.title:
                        next_state = UserState.NEW_ISSUE_TITLE
                        new_issue_repo.create(user.id)
                        new_issue_repo.update(user.id, 'project', project.title)
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Проект: <b>{project.title}</b>', reply_markup=None,
                                              parse_mode='HTML')
                        BOT.send_message(chat.id, 'Введите название задачи:',
                                         reply_markup=create_markup(Button.CANCEL))
                        break
                else:
                    next_state = UserState.NEW_ISSUE_PROJECT
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такого проекта', reply_markup=None)
                    menu_existing(BOT, chat.id)

            case UserState.NEW_ISSUE_ASSIGNEE:
                # is request to jira appropriate here?
                for assignee in jira_imitation.get_assignees():
                    if call.data == assignee.name:
                        next_state = UserState.NEW_ISSUE_DESCRIPTION
                        new_issue_repo.update(user.id, 'assignee', assignee.name)
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Исполнитель: <b>{assignee.name}</b>', reply_markup=None,
                                              parse_mode='HTML')
                        BOT.send_message(chat.id, 'Введите описание задачи',
                                         reply_markup=create_markup(Button.CANCEL))
                        break
                else:
                    next_state = UserState.NEW_ISSUE_ASSIGNEE
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такого исполнителя', reply_markup=None)
                    menu_existing(BOT, chat.id)

            case UserState.MENU | UserState.ISSUE | UserState.STATUS | UserState.NEW_ISSUE_TITLE | \
                 UserState.NEW_ISSUE_DESCRIPTION | UserState.NEW_ISSUE_PREVIEW:
                 pass

            case _:
                BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    except ValueError:
        BOT.send_message(chat.id, "Неизвестное состояние, нажмите /start")

    user_repo.update(user.id, next_state)


if __name__ == '__main__':
    BOT.polling(non_stop=True)
