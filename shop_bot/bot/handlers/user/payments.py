from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, SuccessfulPayment, LabeledPrice
from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from db import crud
from bot.keyboards import user_kb as kb
from bot.texts import successful_payment_text
from utils.decorators import handle_db_errors
from bot.services.invoices import send_order_invoice
from config import PROVIDER_TOKEN

logger = logging.getLogger(__name__)
router = Router()

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await pre_checkout_q.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment: SuccessfulPayment = message.successful_payment
    user_id = message.from_user.id

    try:
        order_id = int(payment.invoice_payload)
    except ValueError as e:
        logger.error(f'❌ Невозможно преобразовать payload в order_id: {payment.invoice_payload}', exc_info=True)
        await message.answer('⚠️ Не удалось обработать номер заказа. Свяжитесь с поддержкой.', reply_markup=kb.main_keyboard())
        return

    try:
        order = await crud.update_order_status(user_id, order_id, 'paid')
    except SQLAlchemyError as e:
        logger.error(f'❌ Ошибка базы данных при установке статуса "paid" для заказа {order_id}', exc_info=True)
        await message.answer(f'❌ Не удалось обновить статус оплаты. Номер заказа: <b>{order_id}</b>. Свяжитесь с поддержкой.', reply_markup=kb.main_keyboard())
        return
    except Exception as e:
        logger.error(f'❌ Неизвестная ошибка при обработке оплаты заказа {order_id}: {e}', exc_info=True)
        await message.answer(f'⚠️ Произошла непредвиденная ошибка. Номер заказа: <b>{order_id}</b>', reply_markup=kb.main_keyboard())
        return
    
    logger.info(f'✅ Оплата заказа № {order_id} прошла успешно!')
    await message.answer(text=successful_payment_text(payment, order), reply_markup=kb.main_keyboard())


@router.callback_query(F.data.startswith('pay_for_the_order_'))
@handle_db_errors()
async def pay_for_the_order(callback: CallbackQuery):
    user_id = callback.from_user.id
    order_id = int(callback.data.split('_')[-1])
    order = await crud.get_order(user_id, order_id)
    logger.info(f'📦 Пользователь {user_id} хочет оплатить заказ №{order.id}.')

    await send_order_invoice(callback.bot, callback.message.chat.id, order, PROVIDER_TOKEN)
    