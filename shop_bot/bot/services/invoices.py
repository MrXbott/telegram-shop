from aiogram.types import LabeledPrice
from aiogram import Bot
import logging

from db.models import Order

logger = logging.getLogger(__name__)

async def send_order_invoice(bot: Bot, chat_id: int, order: Order, provider_token: str) -> None:
    logger.info('ℹ️ Отправка инвойса')
    await bot.send_invoice(
                chat_id=chat_id,
                title=f'Заказ №{order.id}',
                description='Оплата заказа из нашего магазина',
                payload=str(order.id),
                provider_token=provider_token,
                currency='RUB',
                prices=[LabeledPrice(label=f'Оплата заказа №{order.id}', amount=order.total_price * 100)],
                start_parameter=f'order-payment-{order.id}',
                photo_url='',
                photo_height=512,
                photo_width=512,
                photo_size=512,
                need_name=False,
                need_phone_number=False,
                need_email=False,
                is_flexible=False
    )
