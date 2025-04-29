import asyncio
import logging
from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, DBAPIError
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, sessionmaker, max_retries: int = 3, retry_delay: float = 1.0):
        self.sessionmaker = sessionmaker
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def __call__(self, handler: Callable, event: Any, data: Dict[str, Any]):
        attempt = 0
        while attempt < self.max_retries:
            try:
                async with self.sessionmaker() as session:
                    async with session.begin():  
                        data['session'] = session
                        return await handler(event, data)
            except (OperationalError, DBAPIError) as e:
                # ошибки подключения или низкоуровневые ошибки драйвера
                logger.warning(f'DB error on attempt {attempt + 1}: {e}')
                attempt += 1
                await asyncio.sleep(self.retry_delay)
            except Exception as e:
                # любые другие ошибки → откат и пробрасываем вверх
                logger.error(f'Unhandled error: {e}', exc_info=True)
                raise
        raise RuntimeError('Max DB retry attempts exceeded')
