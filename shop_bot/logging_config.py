import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = 'logs'
LOG_FILE = 'bot.log'


def setup_logging(level=logging.INFO):
    os.makedirs(LOG_DIR, exist_ok=True)

    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    date_format = '%d.%m.%Y %H:%M:%S'

    file_handler = RotatingFileHandler(
        filename=os.path.join(LOG_DIR, LOG_FILE),
        maxBytes=1 * 1024 * 1024,  # 1MB
        backupCount=5,             # храним до 5 файлов
        encoding='utf-8'
    )
    
    console_handler = logging.StreamHandler()

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            file_handler,
            console_handler
        ]
    )
