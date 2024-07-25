import enum


class Button(enum.StrEnum):
    # COMMON
    BACK = '⬅️ Назад'
    CANCEL = '❌ Отмена'

    # MENU
    LIST = '📋 Список задач'
    NEW_ISSUE_PROJECT = '📝 Создать задачу'

    # ISSUE FILTER
    NO_FILTER = 'Без фильтра'

    # ISSUE
    STATUS = '📝 Изменить статус'

    # NEW_ISSUE_ASSIGNEE
    NO_ASSIGNEE = 'Без исполнителя'

    # NEW_ISSUE_PREVIEW
    CREATE = '✅ Создать'
