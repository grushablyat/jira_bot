import enum


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
    STATUS_MENU = [TODO, IN_PROGRESS, DONE, CANCEL]

    # NEW_ISSUE_ASSIGNEE
    NO_ONE = 'Без исполнителя'

    # NEW_ISSUE_PREVIEW
    CREATE = 'Создать'
