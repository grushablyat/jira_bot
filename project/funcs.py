from telebot import types

import jira_imitation


def create_markup(*args):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for arg in args:
        markup.add(types.KeyboardButton(arg))

    return markup


def format_issue(issue):
    return f'<b>{issue.title}</b> ({issue.status})\n{issue.assignee}\n\n{issue.description}'


def menu_existing(bot, chat_id):
    bot.send_message(chat_id, 'Выберите существующее действие')


def menu_menu(bot, chat_id):
    bot.send_message(chat_id, 'Выберите нужное действие',
                     reply_markup=create_markup('Просмотреть список задач', 'Создать задачу'))


def menu_list(bot, chat_id):
    bot.send_message(chat_id, 'Выберите задачу',
                     reply_markup=create_markup(*jira_imitation.get_issues_titles(), 'Назад'))


def menu_issue(bot, chat_id, issue):
    bot.send_message(chat_id, format_issue(issue), parse_mode='HTML',
                     reply_markup=create_markup('Изменить статус задачи', 'Назад'))


def menu_status(bot, chat_id):
    bot.send_message(chat_id, 'Выберите новый статус задачи',
                     reply_markup=create_markup('To do', 'In progress', 'Done', 'Отмена'))


def menu_new_issue_project(bot, chat_id):
    bot.send_message(chat_id, 'Выберите проект:',
                     reply_markup=create_markup(*jira_imitation.get_projects_titles(), 'Отмена'))
