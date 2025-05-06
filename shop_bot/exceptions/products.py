class ProductError(Exception):
    """Базовое исключение для ошибок связанных с товаром."""
    pass

class InvalidProductPriceError(ProductError):
    """Ошибка, когда цена товара недопустима."""

    def __init__(self, price: float):
        self.price = price
        super().__init__(f'Недопустимая цена товара: {price}')

class NegativeProductPriceError(ProductError):
    """Ошибка, когда цена товара отрицательная."""

    def __init__(self, price: float):
        self.price = price
        super().__init__(f'Цена товара не может быть отрицательной: {price}')


class TooHighProductPriceError(ProductError):
    """Ошибка, когда цена товара превышает максимально допустимое значение."""

    def __init__(self, price: float):
        self.price = price
        super().__init__(f'Цена товара больше допустимого значения: {price}')

class ProductOutOfStockError(ProductError):
    """Ошибка, когда товара не хватает на складе."""

    def __init__(self, product_name: str):
        self.product_name = product_name
        super().__init__(f'Недостаточно товара: {product_name}')

class NegativeProductQuantityError(ProductError):
    """Ошибка, когда указано отрицательное количество товара."""

    def __init__(self, quantity: int):
        self.quantity = quantity
        super().__init__(f'Количество товара на складе не может быть отрицательным: {quantity}')