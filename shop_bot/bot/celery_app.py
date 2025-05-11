from celery import Celery

from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


if REDIS_PASSWORD:
    redis_uri = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
else:
    redis_uri = f'redis://{REDIS_HOST}:{REDIS_PORT}'

celery_app = Celery(
    'shop_bot',
    broker=f'{redis_uri}/0',
    backend=f'{redis_uri}/1',
    include=['bot.tasks'] 
)

celery_app.conf.timezone = 'Europe/Moscow' 
