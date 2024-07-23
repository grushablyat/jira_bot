from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import testim_jira_api
from button import Button
from config import TG_TOKEN
from service import user_repo, state_repo, current_issue_repo, new_issue_repo
from states import UserState

BOT = TeleBot(token=TG_TOKEN)


def create_markup(*args):
    options = []
    for arg in args:
        options.append(KeyboardButton(arg))

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*options)

    return markup


def create_inline_markup(args, default=None):
    options = []
    for arg in args:
        options.append(InlineKeyboardButton(arg, callback_data=arg))

    markup = InlineKeyboardMarkup()
    markup.add(*options)
    if default:
        markup.add(InlineKeyboardButton(default, callback_data=default))

    return markup


def format_issue(issue):
    return (f'<b><i>Задача</i></b>:\n{issue.key}\n\n'
            f'<b><i>Название</i></b>:\n{issue.fields.summary}\n\n'
            f'<b><i>Исполнитель</i></b>:\n{issue.fields.assignee if issue.fields.assignee else 'Нет'}\n\n'
            f'{f'<b><i>Статус</i></b>:\n{issue.fields.status}\n\n' if issue.fields.status else ''}'
            f'<b><i>Описание</i></b>:\n{issue.fields.description}')


def menu_existing(chat_id, text=None, inline_markup=None):
    BOT.send_message(chat_id, text if text else 'Выберите существующее действие', reply_markup=inline_markup)


def menu_menu(chat_id):
    BOT.send_message(chat_id, 'Выберите нужное действие',
                     reply_markup=create_markup(Button.LIST, Button.NEW_ISSUE_PROJECT))


def menu_list_projects(chat_id):
    BOT.send_message(chat_id, 'Фильтр', reply_markup=create_markup(Button.BACK))
    BOT.send_message(chat_id, 'Выберите проект:',
                     reply_markup=create_inline_markup(testim_jira_api.get_projects_keys(), default='Без фильтра'))


def menu_list_statuses_edit(chat_id, message_id, user_id):
    current_issue = current_issue_repo.get_by_user_id(user_id)

    if current_issue is None:
        BOT.send_message(chat_id, 'Произошла ошибка, нажмите /start')
        return

    pkey = current_issue.project
    BOT.edit_message_text(chat_id=chat_id, message_id=message_id, text=f'Выберите статус:',
                          reply_markup=create_inline_markup(testim_jira_api.get_possible_statuses(pkey),
                                                            default='Без фильтра'))


def menu_list_statuses_new(chat_id, user_id):
    current_issue = current_issue_repo.get_by_user_id(user_id)

    if current_issue is None:
        BOT.send_message(chat_id, 'Произошла ошибка, нажмите /start')
        return

    pkey = current_issue.project
    BOT.send_message(chat_id, 'Выберите статус:',
                     reply_markup=create_inline_markup(testim_jira_api.get_possible_statuses(pkey),
                                                       default='Без фильтра'))


def menu_list_issues(chat_id, user_id):
    user = user_repo.get_by_id(user_id)

    if user is None:
        BOT.send_message(chat_id, 'Пользователь не зарегистрирован, обратитесь к администратору')
        return
    elif user.is_manager:
        user = None
    else:
        user = user.jira_username

    filtering_issue = current_issue_repo.get_by_user_id(user_id)
    params = [user]
    filters = []

    if filtering_issue is not None:
        params.append(filtering_issue.project)
        if filtering_issue.project is not None:
            filters.append(f'Проект: {filtering_issue.project}')
        params.append(filtering_issue.status)
        if filtering_issue.status is not None:
            filters.append(f'Статус: {filtering_issue.status}')
        if len(filters) > 0:
            filters.append('')
            filters.insert(0, 'Фильтры:')

    return [params, filters]


def menu_list_issues_edit(chat_id, user_id, message_id):
    params, filters = menu_list_issues(chat_id, user_id)
    BOT.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=f'{'\n'.join(filters)}\nВыберите задачу:',
                          reply_markup=create_inline_markup(testim_jira_api.get_issues_keys(*params)))


def menu_list_issues_new(chat_id, user_id):
    params, filters = menu_list_issues(chat_id, user_id)
    BOT.send_message(chat_id, f'{'\n'.join(filters)}\nВыберите задачу:',
                     reply_markup=create_inline_markup(testim_jira_api.get_issues_keys(*params)))


def menu_list_issues_back(chat_id, user_id):
    params, filters = menu_list_issues(chat_id, user_id)
    BOT.send_message(chat_id, 'Список задач', reply_markup=create_markup(Button.BACK))
    BOT.send_message(chat_id, f'{'\n'.join(filters)}\nВыберите задачу:',
                     reply_markup=create_inline_markup(testim_jira_api.get_issues_keys(*params)))


def menu_issue(chat_id, issue):
    BOT.send_message(chat_id, format_issue(issue), parse_mode='HTML',
                     reply_markup=create_markup(Button.STATUS, Button.BACK))


def menu_new_issue_project(chat_id):
    BOT.send_message(chat_id, 'Список проектов:',
                     reply_markup=create_inline_markup(testim_jira_api.get_projects_keys()))


def menu_new_issue_assignee(chat_id, user_id):
    new_issue = new_issue_repo.get_by_user_id(user_id)

    if new_issue is None:
        BOT.send_message(chat_id, 'Произошла ошибка, нажмите /start')
        return

    pkey = new_issue.project
    BOT.send_message(chat_id, 'Список исполнителей:',
                     reply_markup=create_inline_markup(testim_jira_api.get_assignable_users(pkey)))


@BOT.message_handler(commands=['start'])
def start(message):
    chat = message.chat
    user = message.from_user

    if user_repo.get_by_id(user.id) is None:
        BOT.send_message(chat.id, 'Пользователь не зарегистрирован, обратитесь к администратору',
                         reply_markup=create_markup(Button.BACK))
        return

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

    current_state = state_repo.get_by_user_id(user.id)

    if current_state is None:
        BOT.send_message(chat.id, "Произошла ошибка, нажмите /start")
        return

    next_state = UserState.MENU

    try:
        match current_state:
            case UserState.MENU:
                if message.text == Button.LIST:
                    next_state = UserState.LIST_PROJECTS
                    menu_list_projects(chat.id)
                elif message.text == Button.NEW_ISSUE_PROJECT:
                    this_user = user_repo.get_by_id(user.id)
                    if this_user is None:
                        BOT.send_message(chat.id, 'Пользователь не зарегистрирован, обратитесь к администратору')
                    elif this_user.is_manager:
                        next_state = UserState.NEW_ISSUE_PROJECT
                        BOT.send_message(chat.id, 'Выберите проект', reply_markup=create_markup(Button.CANCEL))
                        menu_new_issue_project(chat.id)
                    else:
                        next_state = UserState.MENU
                        BOT.send_message(chat.id, 'Функция создания задачи доступна только менеджерам')
                else:
                    next_state = UserState.MENU
                    menu_existing(chat.id)

            case UserState.LIST_PROJECTS:
                BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                      text=f'Выберите проект', reply_markup=None)
                if message.text == Button.BACK:
                    next_state = UserState.MENU
                    menu_menu(chat.id)
                else:
                    next_state = UserState.LIST_PROJECTS

                    BOT.send_message(chat.id, 'Выберите существующий проект')
                    menu_list_projects(chat.id)

            case UserState.LIST_STATUSES:
                BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                      text=f'Выберите статус', reply_markup=None)
                if message.text == Button.BACK:
                    current_issue_repo.delete(user.id)
                    next_state = UserState.MENU
                    menu_menu(chat.id)
                else:
                    next_state = UserState.LIST_STATUSES

                    BOT.send_message(chat.id, 'Выберите существующий статус',
                                     reply_markup=create_markup(Button.BACK))
                    menu_list_statuses_new(chat.id, user.id)

            case UserState.LIST_ISSUES:
                BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                      text=f'Выберите задачу', reply_markup=None)
                if message.text == Button.BACK:
                    current_issue_repo.delete(user.id)
                    next_state = UserState.MENU
                    menu_menu(chat.id)
                else:
                    next_state = UserState.LIST_ISSUES

                    BOT.send_message(chat.id, 'Выберите существующую задачу',
                                     reply_markup=create_markup(Button.BACK))
                    menu_list_issues_new(chat.id, user.id)

            case UserState.ISSUE:
                if message.text == Button.STATUS:
                    next_state = UserState.STATUS
                    issue = current_issue_repo.get_by_user_id(user.id)
                    if issue is not None:
                        BOT.send_message(chat.id, 'Изменение статуса задачи',
                                         reply_markup=create_markup(Button.CANCEL))
                        BOT.send_message(chat.id, 'Выберите операцию',
                                         reply_markup=create_inline_markup(
                                             testim_jira_api.get_possible_transitions(issue.key)))
                    else:
                        next_state = UserState.LIST_ISSUES
                        BOT.send_message(chat.id, 'Задача не найдена или соединение с Jira прервано')
                        current_issue_repo.update(user.id, 'issue_key', None)
                        menu_list_issues_back(chat.id, user.id)

                elif message.text == Button.BACK:
                    next_state = UserState.LIST_ISSUES
                    current_issue_repo.update(user.id, 'issue_key', None)
                    menu_list_issues_back(chat.id, user.id)
                else:
                    next_state = UserState.ISSUE
                    menu_existing(chat.id)

            case UserState.STATUS:
                if message.text == Button.CANCEL:
                    BOT.edit_message_text(chat_id=chat.id, message_id=message.message_id - 1,
                                          text=f'Статус не изменен', reply_markup=None)
                    next_state = UserState.ISSUE
                    current_issue = current_issue_repo.get_by_user_id(user.id)

                    if current_issue is not None:
                        issue = testim_jira_api.get_issue_by_key(current_issue.key)

                        if issue is None:
                            next_state = UserState.LIST_ISSUES
                            BOT.send_message(chat.id, 'Задача не найдена или соединение с Jira прервано')
                            current_issue_repo.update(user.id, 'issue_key', None)
                            menu_list_issues_back(chat.id, user.id)
                        else:
                            menu_issue(chat.id, issue)
                    else:
                        next_state = UserState.LIST_ISSUES
                        current_issue_repo.delete(user.id)
                        menu_existing(chat.id, "Произошла ошибка, попробуйте снова")
                        current_issue_repo.update(user.id, 'issue_key', None)
                        menu_list_issues_back(chat.id, user.id)
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
                    menu_new_issue_assignee(chat.id, user.id)

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
                    menu_new_issue_assignee(chat.id, user.id)

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
                        dictionary = issue.to_dict()

                        if dictionary is None:
                            BOT.send_message(chat.id, 'Произошла ошибка, нажмите /start')
                            return

                        issue = testim_jira_api.create_issue(dictionary, issue.assignee)
                        if issue is None:
                            next_state = UserState.MENU
                            BOT.send_message(chat.id, 'Задача не найдена или соединение с Jira прервано')
                            menu_menu(chat.id)
                        else:
                            current_issue_repo.create(user.id)
                            current_issue_repo.update(user.id, 'issue_key', issue.raw.get('key'))
                            menu_issue(chat.id, issue)
                    else:
                        next_state = UserState.MENU
                        menu_existing(chat.id, 'Произошла ошибка, попробуйте снова')
                        menu_menu(chat.id)

            case _:
                BOT.send_message(chat.id, "Произошла ошибка, нажмите /start")

    except ValueError:
        BOT.send_message(chat.id, "Произошла ошибка, нажмите /start")

    state_repo.update(user.id, next_state)


@BOT.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat = call.message.chat
    user = call.from_user

    current_state = state_repo.get_by_user_id(user.id)

    if current_state is None:
        BOT.send_message(chat.id, "Произошла ошибка, нажмите /start")
        return

    next_state = UserState.MENU

    try:
        match current_state:
            case UserState.LIST_PROJECTS:
                for pkey in testim_jira_api.get_projects_keys():
                    if call.data == pkey:
                        next_state = UserState.LIST_STATUSES
                        current_issue_repo.create(user.id)
                        current_issue_repo.update(user.id, 'project', pkey)
                        menu_list_statuses_edit(chat.id, call.message.message_id, user.id)
                        break
                else:
                    if call.data == 'Без фильтра':
                        next_state = UserState.LIST_STATUSES
                        current_issue_repo.create(user.id)
                        menu_list_statuses_edit(chat.id, call.message.message_id, user.id)
                    else:
                        # UNREACHABLE
                        next_state = UserState.LIST_PROJECTS
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Нет такого проекта', reply_markup=None)
                        menu_existing(chat.id)

            case UserState.LIST_STATUSES:
                current_issue = current_issue_repo.get_by_user_id(user.id)

                if current_issue is None:
                    BOT.send_message(chat.id, 'Произошла ошибка, нажмите /start')
                    return

                pkey = current_issue.project

                for status in testim_jira_api.get_possible_statuses(pkey):
                    if call.data == status:
                        next_state = UserState.LIST_ISSUES
                        # current_issue_repo.update(user.id, 'status', f'\'{status}\'')
                        current_issue_repo.update(user.id, 'status', status)
                        menu_list_issues_edit(chat.id, user.id, call.message.message_id)
                        break
                else:
                    if call.data == 'Без фильтра':
                        next_state = UserState.LIST_ISSUES
                        current_issue_repo.update(user.id, 'status', None)

                        menu_list_issues_edit(chat.id, user.id, call.message.message_id)
                    else:
                        # UNREACHABLE
                        next_state = UserState.LIST_ISSUES
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Нет такого статуса', reply_markup=None)
                        menu_existing(chat.id)

            case UserState.LIST_ISSUES:
                for issue in testim_jira_api.get_issues():
                    if call.data == issue.raw.get('key'):
                        next_state = UserState.ISSUE
                        current_issue_repo.update(user.id, 'issue_key', issue.raw.get('key'))
                        BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                              text=f'Список задач', reply_markup=None)
                        menu_issue(chat.id, issue)
                        break
                else:
                    # UNREACHABLE
                    next_state = UserState.LIST_ISSUES
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такой задачи', reply_markup=None)
                    menu_existing(chat.id)

            case UserState.STATUS:
                issue = current_issue_repo.get_by_user_id(user.id)
                if issue is None:
                    next_state = UserState.LIST_ISSUES
                    current_issue_repo.update(user.id, 'issue_key', None)
                    menu_existing(chat.id, "Произошла ошибка, попробуйте снова")
                    menu_list_issues_back(chat.id, user.id)
                elif call.data in testim_jira_api.get_possible_transitions(issue.key):
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Операция: <b>{call.data}</b>', reply_markup=None,
                                          parse_mode='HTML')
                    next_state = UserState.ISSUE
                    current_issue = current_issue_repo.get_by_user_id(user.id)

                    if current_issue is not None:
                        testim_jira_api.update_issue_status(current_issue.key, call.data)
                        issue = testim_jira_api.get_issue_by_key(current_issue.key)

                        if issue is None:
                            next_state = UserState.LIST_ISSUES
                            current_issue_repo.update(user.id, 'issue_key', None)
                            BOT.send_message(chat.id, 'Задача не найдена или соединение с Jira прервано')
                            menu_list_issues_back(chat.id, user.id)
                        else:
                            menu_issue(chat.id, issue)
                    else:
                        next_state = UserState.LIST_ISSUES
                        current_issue_repo.update(user.id, 'issue_key', None)
                        menu_existing(chat.id, "Произошла ошибка, попробуйте снова")
                        menu_list_issues_back(chat.id, user.id)
                else:
                    next_state = UserState.ISSUE
                    BOT.edit_message_text(chat_id=chat.id, message_id=call.message.message_id,
                                          text=f'Нет такого статуса, нажмите /start', reply_markup=None)
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
                new_issue = new_issue_repo.get_by_user_id(user.id)

                if new_issue is None:
                    BOT.send_message(chat.id, 'Произошла ошибка, нажмите /start')
                    return

                pkey = new_issue.project

                for assignee in testim_jira_api.get_assignable_users(pkey):
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
                BOT.send_message(chat.id, "Произошла ошибка, нажмите /start")

    except ValueError:
        BOT.send_message(chat.id, "Произошла ошибка, нажмите /start")

    state_repo.update(user.id, next_state)


if __name__ == '__main__':
    BOT.polling(non_stop=True)
