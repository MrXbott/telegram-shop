import os
from dotenv import load_dotenv

load_dotenv()

PYTHONPATH = os.getenv('PYTHONPATH', '.')
BOT_TOKEN = os.getenv('BOT_TOKEN')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_FOLDER = os.getenv('MEDIA_FOLDER')
MEDIA_FOLDER_PATH = os.path.join(BASE_DIR, MEDIA_FOLDER)

POSTGRES_URL=os.getenv('POSTGRES_URL')
POSTGRES_URL_SYNC=os.getenv('POSTGRES_URL_SYNC')

REDIS_HOST=os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT=os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')
UNPAID_ORDER_TIMEOUT = int(os.getenv('UNPAID_ORDER_TIMEOUT', 1800))

EXCHANGE_RATES_API = os.getenv('EXCHANGE_RATES_API')
EXCHANGE_RATE_UPDATE_INTERVAL = int(os.getenv('EXCHANGE_RATE_UPDATE_INTERVAL'))
