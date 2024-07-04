import enum


class UserState(enum.IntEnum):
    MENU = 0

    LIST = 11
    ISSUE = 12
    STATUS = 13

    NEW_ISSUE_PROJECT = 21
    NEW_ISSUE_TITLE = 22
    NEW_ISSUE_ASSIGNEE = 23
    NEW_ISSUE_DESCRIPTION = 24
    NEW_ISSUE_PREVIEW = 25
