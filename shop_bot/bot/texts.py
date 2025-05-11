from typing import List
from aiogram.types import SuccessfulPayment
from db.models import Product, Order, OrderItem
from db.cart import ProductInCart

def product_text(product: Product) -> str:
    return f'<b>{product.name}</b>\nЦена: {product.price}₽'

def cart_text(products: List[ProductInCart]) -> str:
    total = sum(product.product.price * product.quantity for product in products)
    lines = [f'• {product.product.name} - {product.product.price}₽ - {product.quantity} шт.' for product in products]
    return 'Товары в корзине: \n' + '\n'.join(lines) + f'\n\n<b>Итого:</b> {total}₽'

def order_text(order: Order, items: List[OrderItem]) -> str:
    text = (
        f'Заказ <b>№{order.id}</b>\n'
        f'Статус: <b>{order.status.status_name}</b>\n'
        f'Оформлен: <b>{order.created.strftime("%d.%m.%Y %H:%M")}</b>\n'
        f'Адрес доставки: <b>{order.address.address}</b>\n'
        f'Заказчик: <b>{order.name}</b>\n'
        f'Телефон: <b>{order.phone}</b>\n'
        f'Стоимость: <b>{order.total_price}₽</b>\n\n'
        f'Товары в заказе: \n'
        )
    lines = [f'<b>• {item.product.name}</b> - {item.product.price}₽ x {item.quantity} шт. = <b>{item.product.price * item.quantity}₽</b>' for item in items]
    return text + '\n'.join(lines)

def successful_payment_text(payment: SuccessfulPayment, order: Order):
    return (f'✅ Оплата прошла успешно!\n\n'
            f'Номер заказа: <b>{order.id}</b>\n'
            f'Статус: <b>{order.status.status_name}</b>\n'
            f'Сумма: <b>{payment.total_amount / 100:.2f} {payment.currency}</b>\n'
            )
