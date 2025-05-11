from aiogram.types import Message, PreCheckoutQuery, SuccessfulPayment
from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

from db import crud
from keyboards import user_kb as kb
from texts import successful_payment_text


logger = logging.getLogger(__name__)
router = Router()

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await pre_checkout_q.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, session: AsyncSession):
    payment: SuccessfulPayment = message.successful_payment

    try:
        order_id = int(payment.invoice_payload)
    except ValueError as e:
        logger.error(f'❌ Невозможно преобразовать payload в order_id: {payment.invoice_payload}', exc_info=True)
        await message.answer('⚠️ Не удалось обработать номер заказа. Свяжитесь с поддержкой.', reply_markup=kb.main_keyboard())
        return

    try:
        order = await crud.order_set_status_paid(session, order_id)
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