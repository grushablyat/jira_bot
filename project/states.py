import enum


class UserState(enum.IntEnum):
    MENU = 0
    ERROR = 1

    LIST_PROJECTS = 11
    LIST_STATUSES = 12
    LIST_ISSUES = 13
    ISSUE = 14
    STATUS = 15

    NEW_ISSUE_PROJECT = 21
    NEW_ISSUE_SUMMARY = 22
    NEW_ISSUE_ASSIGNEE = 23
    NEW_ISSUE_DESCRIPTION = 24
    NEW_ISSUE_PREVIEW = 25
