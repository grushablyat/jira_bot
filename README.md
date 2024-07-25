# Telegram-бот для управления задачами Jira

## Конфигурация `project/config.py`

```python
# project/config.py

LOG_FILE = 'LOG_FILE'

TG_TOKEN = 'TG_TOKEN'

# Jira config (jira user should have administrator rights)
JIRA_USERNAME = 'JIRA_USERNAME'
JIRA_PASSWORD = 'JIRA_PASSWORD'
JIRA_URL = 'JIRA_URL'

# Database connectivity config
DBC = {
    'username': 'USERNAME',
    'password': 'PASSWORD',
    'host': 'HOST',
    'port': PORT,
    'database': 'DATABASE',
}
```

## Структура БД

```mermaid
erDiagram
    users {
        decimal id
        varchar jira_username
        boolean is_manager
    }
    users ||--o| state : has
    users ||--o| current_issue : might-have
    users ||--o| new_issue : might-have
    
    state {
        decimal user_id
        int state
    }
    
    current_issue {
        decimal user_id
        varchar project
        varchar status
        varchar issue_key
    }
    
    new_issue {
        decimal user_id
        varchar project
        varchar summary
        varchar assignee
        text description
    }
```

## Требуемые пакеты

1. jira
2. psycopg2
3. requests
4. telebot (pyTelegramBotAPI)
