import aiohttp
from datetime import datetime, timedelta
import logging
import json

from exceptions.bot.payments import TelegramPaymentLimitError
from config import EXCHANGE_RATES_API, EXCHANGE_RATE_UPDATE_INTERVAL

logger = logging.getLogger(__name__)

class ExchangeRateService:
    def __init__(self):
        self._cache = {}
        self._last_updated = None
        self._url = EXCHANGE_RATES_API
        self._timedelta = timedelta(minutes=EXCHANGE_RATE_UPDATE_INTERVAL)

    async def get_exchange_rate(self, currency_code: str) -> float:
        if self._last_updated is None or datetime.now() - self._last_updated > self._timedelta:
            await self._update_rates(currency_code)
        return self._cache.get(currency_code)

    async def _update_rates(self, currency_code: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url) as response:

                if response.status != 200:
                    raise Exception(f'Failed to fetch exchange rates: {response.status}')
                
                text = await response.text()
                data = json.loads(text)
                currency_value = data['Valute'][currency_code]['Value']
                self._cache[currency_code] = currency_value
                self._last_updated = datetime.now()


def validate_payment_amount(
    payment_amount: int,
    currency_code: str,
    currency_rate: float,
    min_usd: float = 1.0,
    max_usd: float = 10000.0,
    buffer: float = 0.05  
) -> None:
    """
        Checks whether the payment amount fits within Telegram's allowed limits.
        
        :param payment_amount: amount in the smallest units of the specified currency (e.g., in kopecks 14900 = 149.00₽)
        :param currency_rate: current USD to specified currency exchange rate
        :param currency_code: currency code (e.g., RUB)
        :param min_usd: minimum allowed amount in USD
        :param max_usd: maximum allowed amount in USD
        :param buffer: percentage buffer to account for exchange rate fluctuations
        :raises TelegramPaymentLimitError: if the amount is outside the allowed range
    """

    safe_min = int((min_usd * currency_rate * (1 + buffer)) * 100) 
    safe_max = int((max_usd * currency_rate * (1 - buffer)) * 100)

    if not (safe_min <= payment_amount <= safe_max):
        raise TelegramPaymentLimitError(payment_amount, currency_code, safe_min, safe_max)
