import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = 'logs'
BOT_LOG_FILE = 'bot.log'
ADMIN_LOG_FILE = 'admin.log'

def setup_logging(level=logging.DEBUG):
    os.makedirs(LOG_DIR, exist_ok=True)

    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    date_format = '%d.%m.%Y %H:%M:%S'
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    bot_file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, BOT_LOG_FILE),
        maxBytes=1 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    bot_file_handler.setFormatter(formatter)

    admin_file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, ADMIN_LOG_FILE),
        maxBytes=1 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    admin_file_handler.setFormatter(formatter)

    bot_logger = logging.getLogger('bot')
    bot_logger.setLevel(level)
    bot_logger.addHandler(bot_file_handler)
    bot_logger.propagate = True 

    admin_logger = logging.getLogger('admin')
    admin_logger.setLevel(level)
    admin_logger.addHandler(admin_file_handler)
    admin_logger.propagate = True

    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
