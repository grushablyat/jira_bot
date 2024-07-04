import enum

from telebot import types

import jira_imitation


def create_markup(*args):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for arg in args:
        markup.add(types.KeyboardButton(arg))

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

    # LIST

    # ISSUE
    STATUS = 'Изменить статус задачи'

    # STATUS
    TODO = 'To do'
    IN_PROGRESS = 'In progress'
    DONE = 'Done'


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
