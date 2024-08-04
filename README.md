# Telegram-бот для управления задачами Jira

## Конфигурация `bot/config.py`

```python
# bot/config.py

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
    'host': 'DB_HOST',
    'port': DB_PORT,
    'database': 'DATABASE',
}

# Notifier config
NOTIFY = {
    'host': 'NOTIFIER_HOST',
    'port': NOTIFIER_PORT,
}
```

## Настройка уведомителя

Для начала убедитесь, что все действия по [настройке обработчика событий Jira](https://github.com/grushablyat/JiraEventHandler#%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0) выполнены

Если вы запускаете уведомителя на публичном адресе, дальнейшая настройка не требуется \
Если же уведомитель запускается локально, следует настроить туннелирование с помощью утилиты ngrok (или аналогов)

```powershell
ngrok http --domain=YOUR_NGROK_DOMAIN http://NOTIFIER_HOST:NOTIFIER_PORT
```

В этом случае в обработчике событий Jira в качестве URL необходимо указать ```YOUR_NGROK_DOMAIN```
