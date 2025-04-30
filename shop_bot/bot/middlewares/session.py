import asyncio
import logging
from aiogram import BaseMiddleware
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
            async with self.sessionmaker() as session:
                data['session'] = session
                return await handler(event, data)
