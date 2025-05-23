from aiogram import Bot
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
import logging

from bot.celery_app import celery_app
from db.models import Order, OrderItem, OrderStatus
import bot.keyboards as kb
from config import BOT_TOKEN, POSTGRES_URL


logger = logging.getLogger(__name__)

@celery_app.task
def cancel_unpaid_order(user_id: int, order_id: int):
    import asyncio

    async def cancel_order():
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select, update

        logger.info(f'🚀 Запущена задача отмены заказа: user_id={user_id}, order_id={order_id}')

        async_engine = create_async_engine(POSTGRES_URL, echo=False)
        async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

        bot = Bot(token=BOT_TOKEN)
        try:
            async with async_session_maker() as session:
                try:
                    result = await session.execute(
                                select(Order)
                                .where(Order.user_id==user_id, Order.id==order_id)
                                .options(selectinload(Order.items).selectinload(OrderItem.product))
                                )
                    order =  result.scalar_one() 
                except NoResultFound as e:
                    logger.error(f'❌ Заказ №{order_id} не найден: {e}')

                logger.info(f'📦 Найден заказ: id={order.id}, статус={order.status_id}')

                try:
                    result = await session.execute(select(OrderStatus).filter(OrderStatus.status == 'waiting_for_payment'))
                    waiting_for_payment_status = result.scalar_one()
                except NoResultFound as e:
                    logger.error(f'❌ Статус заказа waiting_for_payment не найден: {e}')
                except MultipleResultsFound as e:
                    logger.error(f'❌ Найдено несколько результатов для статуса waiting_for_payment: {e}')

                logger.info(f'📦 Найден статус waiting_for_payment: id={waiting_for_payment_status.id}')

                result = await session.execute(select(OrderStatus).filter(OrderStatus.status == 'cancelled'))
                cancelled_status = result.scalar_one()
                logger.info(f'📦 Найден статус cancelled: id={cancelled_status.id}')

                if order.status_id == waiting_for_payment_status.id:
                    await session.execute(update(Order).where(Order.id == order_id).values(status_id=cancelled_status.id))
                    await session.commit()
                    logger.info(f'ℹ️ Заказ №{order.id} отменен: новый статус = {cancelled_status.status}, id = {cancelled_status.id}')

                    await session.refresh(order)

                    for item in order.items:
                        item.product.quantity_in_stock += item.quantity

                    await session.commit()
                    logger.info(f'✅❌ Заказ №{order.id} успешно отменён и товары возвращены на склад.')

                    await bot.send_message(user_id, f'❌ Ваш заказ №{order_id} был автоматически отменён из-за отсутствия оплаты.', reply_markup=kb.menu_keyboard())
                else:
                    logger.info(f'ℹ️ Заказ {order.id} не в статусе ожидания оплаты. Пропуск.')
        except Exception as e:
            logger.error(f'❌ Ошибка при отмене заказа №{order_id}: {e}')
        finally:
            await bot.session.close()

    asyncio.run(cancel_order())