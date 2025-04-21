def product_text(product):
    return f'<b>{product.name}</b>\nЦена: {product.price}₽'

def cart_text(items):
    total = sum(item.product.price for item in items)
    lines = [f'• {item.product.name} — {item.product.price}₽' for item in items]
    return 'Товары в корзине: \n' + '\n'.join(lines) + f'\n\n<b>Итого:</b> {total}₽'
