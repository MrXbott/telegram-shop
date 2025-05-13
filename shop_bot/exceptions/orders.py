class OrderError(Exception):
    """Базовое исключение для ошибок при оформлении заказа."""
    pass

class OrderNotFound(OrderError):
    """Исключение, когда заказ по указанному id не найден."""

    def __init__(self, user_id: int,  order_id: int):
        self.user_id = user_id
        self.order_id = order_id
        super().__init__(f'Заказ с id {order_id} для пользователя с id {user_id} не найден.')

class InvalidOrderTotalPriceError(OrderError):
    """Исключение, когда общая цена заказа недопустима."""

    def __init__(self, price: float):
        self.price = price
        super().__init__(f'Цена заказа не может быть отрицательной: {price}')

