import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.exceptions import TelegramAPIError
from typing import Callable, Dict, Awaitable, Any

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramAPIError as tg_err:
            logger.warning(f'Telegram API error: {tg_err}', exc_info=True)
            raise
        except Exception as e:
            logger.error(f'Unhandled error in handler: {e}', exc_info=True)
            raise
