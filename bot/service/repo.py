import logging

from psycopg2 import connect, OperationalError

from bot.config import DBC

db_logger = logging.getLogger(__name__)


def create_connection():
    connection = None
    try:
        connection = connect(
            database=DBC['database'],
            user=DBC['username'],
            password=DBC['password'],
            host=DBC['host'],
            port=DBC['port'],
        )
    except OperationalError as e:
        db_logger.error(e)

    return connection
