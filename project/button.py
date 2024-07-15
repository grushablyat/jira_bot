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
    TODO = 'Reopen'
    IN_PROGRESS = 'In progress'
    DONE = 'Done'

    # NEW_ISSUE_ASSIGNEE
    NO_ONE = 'Без исполнителя'

    # NEW_ISSUE_PREVIEW
    CREATE = 'Создать'


# STATUS_MENU = [Button.TODO, Button.IN_PROGRESS, Button.DONE, Button.CANCEL]
STATUS_MENU = [Button.TODO, Button.DONE, Button.CANCEL]
