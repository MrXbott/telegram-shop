from typing import List
from db.models import Product
from db.cart import ProductInCart

def product_text(product: Product) -> str:
    return f'<b>{product.name}</b>\nЦена: {product.price}₽'

def cart_text(products: List[ProductInCart]) -> str:
    total = sum(product.product.price * product.quantity for product in products)
    lines = [f'• {product.product.name} - {product.product.price}₽ - {product.quantity} шт.' for product in products]
    return 'Товары в корзине: \n' + '\n'.join(lines) + f'\n\n<b>Итого:</b> {total}₽'
