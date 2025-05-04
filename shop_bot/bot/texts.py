from typing import List
from db.models import Product, Order, OrderItem
from db.cart import ProductInCart

def product_text(product: Product) -> str:
    return f'<b>{product.name}</b>\nЦена: {product.price}₽'

def cart_text(products: List[ProductInCart]) -> str:
    total = sum(product.product.price * product.quantity for product in products)
    lines = [f'• {product.product.name} - {product.product.price}₽ - {product.quantity} шт.' for product in products]
    return 'Товары в корзине: \n' + '\n'.join(lines) + f'\n\n<b>Итого:</b> {total}₽'

def order_text(order: Order, items: List[OrderItem]) -> str:
    text = f'Заказ <b>№{order.id}</b> \nОформлен: <b>{order.created.strftime("%d.%m.%Y %H:%M")}</b> \nСтоимость: <b>{order.total_price}₽</b> \n\nТовары в заказе: \n'
    lines = [f'• {item.product.name} - {item.product.price}₽ - {item.quantity} шт.' for item in items]
    return text + '\n'.join(lines)