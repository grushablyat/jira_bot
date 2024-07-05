import enum

from telebot import types

import jira_imitation


def create_markup(*args):
    actions = []
    for arg in args:
        actions.append(types.KeyboardButton(arg))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*actions)

    return markup


def format_issue(issue):
    return f'<b>{issue.title}</b> ({issue.status})\n{issue.assignee}\n\n{issue.description}'


class Button(enum.StrEnum):
    # COMMON
    BACK = 'Назад'
    CANCEL = 'Отмена'

    # MENU
    LIST = 'Просмотреть список задач'
    NEW_ISSUE_PROJECT = 'Создать задачу'

    # ISSUE
    STATUS = 'Изменить статус задачи'

    # STATUS
    TODO = 'To do'
    IN_PROGRESS = 'In progress'
    DONE = 'Done'

    # NEW_ISSUE_ASSIGNEE
    NO_ONE = 'Без исполнителя'

    # NEW_ISSUE_PREVIEW
    CREATE = 'Создать'


def menu_existing(bot, chat_id):
    bot.send_message(chat_id, 'Выберите существующее действие')


def menu_menu(bot, chat_id):
    bot.send_message(chat_id, 'Выберите нужное действие',
                     reply_markup=create_markup(Button.LIST, Button.NEW_ISSUE_PROJECT))


def menu_list(bot, chat_id):
    bot.send_message(chat_id, 'Выберите задачу',
                     reply_markup=create_markup(*jira_imitation.get_issues_titles(), Button.BACK))


def menu_issue(bot, chat_id, issue):
    bot.send_message(chat_id, format_issue(issue), parse_mode='HTML',
                     reply_markup=create_markup(Button.STATUS, Button.BACK))


def menu_status(bot, chat_id):
    bot.send_message(chat_id, 'Выберите новый статус задачи',
                     reply_markup=create_markup(Button.TODO, Button.IN_PROGRESS, Button.DONE, Button.CANCEL))


def menu_new_issue_project(bot, chat_id):
    bot.send_message(chat_id, 'Выберите проект:',
                     reply_markup=create_markup(*jira_imitation.get_projects_titles(), Button.CANCEL))


def menu_new_issue_title(bot, chat_id):
    bot.send_message(chat_id, 'Введите название задачи:',
                     reply_markup=create_markup(Button.CANCEL))


def menu_new_issue_assignee(bot, chat_id):
    bot.send_message(chat_id, 'Выберите исполнителя',
                     reply_markup=create_markup(*jira_imitation.get_assignees_names(), Button.NO_ONE, Button.CANCEL))


def menu_new_issue_description(bot, chat_id):
    bot.send_message(chat_id, 'Введите описание задачи',
                     reply_markup=create_markup(Button.CANCEL))


def menu_new_issue_preview(bot, chat_id, issue):
    bot.send_message(chat_id, format_issue(issue), parse_mode='HTML')
    bot.send_message(chat_id, 'Подтвердите создание задачи',
                     reply_markup=create_markup(Button.CREATE, Button.CANCEL))
