class OrderStatusError(Exception):
    """Базовый класс ошибок, связанных со статусами заказов."""
    pass

class OrderStatusNotFound(OrderStatusError):
    def __init__(self, status_code: str):
        self.status_code = status_code
        super().__init__(f'Статус с кодом {status_code} не найден.')

class MultipleOrderStatusesFound(OrderStatusError):
    def __init__(self, status_code: str):
        self.status_code = status_code
        super().__init__(f'Найдено несколько статусов с кодом {status_code}.')
