from bot.celery_app import celery_app

from db.init import async_session_maker
from db import crud


@celery_app.task
def cancel_unpaid_order(user_id: int, order_id: int):
    import asyncio

    async def cancel():
        try:
            async with async_session_maker() as session:
                # to do: ловить исключение если заказ не найден
                order = await crud.get_order(session, user_id, order_id)

                # to do: ловить исключение если статус не найден
                waiting_for_payment_status_id = await crud.get_status_id(session, 'waiting_for_payment')

                if order.status_id == waiting_for_payment_status_id:
                    order = await crud.update_order_status(session, order_id, 'cancelled')
                    await crud.return_cancelled_order_items(session, order_id)
        except Exception as e:
            print(f'[cancel] ❗ Ошибка при отмене заказа: {e}', flush=True)

    asyncio.run(cancel())
