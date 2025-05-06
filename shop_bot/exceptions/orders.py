class OrderError(Exception):
    """Базовое исключение для ошибок при оформлении заказа."""
    pass

class InvalidOrderTotalPriceError(OrderError):
    """Ошибка, когда общая цена заказа недопустима."""

    def __init__(self, price: float):
        self.price = price
        super().__init__(f'Цена заказа не может быть отрицательной: {price}')
