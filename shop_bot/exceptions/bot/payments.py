class TelegramPaymentLimitError(Exception):
    """Exception raised when the order amount exceeds Telegram's allowed limits"""

    def __init__(self, amount: int, currency_code: str, min_amount: int, max_amount: int):
        self.amount = amount / 100
        self.currency_code = currency_code
        self.min_amount = min_amount / 100
        self.max_amount = max_amount / 100
        super().__init__(self.__str__())

    def __str__(self):
        return (
            f'Сумма {self.amount:.2f} вне допустимых границ Telegram: '
            f'от {self.min_amount:.2f} до {self.max_amount:.2f}'
        )