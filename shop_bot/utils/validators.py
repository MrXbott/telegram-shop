import re


PHONE_REGEX = re.compile(r'^(?:\+7|8)?\s*\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$')

def is_valid_phone(phone: str) -> bool:
    return PHONE_REGEX.match(phone.strip()) is not None


PHONE_CLEAN_PATTERN = re.compile(r'\D+')

def normalize_phone(phone: str) -> str:
    """
    Приводит номер телефона к формату +7XXXXXXXXXX.
    Принимает различные варианты ввода: с пробелами, скобками, дефисами и т.д.
    """
    digits = ''.join(PHONE_CLEAN_PATTERN.sub('', phone))

    if digits.startswith('8') and len(digits) == 11:
        digits = '7' + digits[1:]
    elif digits.startswith('7') and len(digits) == 11:
        pass
    elif digits.startswith('9') and len(digits) == 10:
        digits = '7' + digits
    else:
        raise ValueError('Неверный формат номера')

    return f'+{digits}'


def is_valid_name(name: str) -> bool:
    """Проверяет, что имя состоит из букв, может содержать пробелы и не слишком короткое."""
    name = name.strip()
    return bool(re.fullmatch(r'[А-Яа-яA-Za-z\s\-]{2,50}', name))


def is_valid_address(address: str) -> bool:
    """Простая проверка: адрес должен быть не короче 10 символов и содержать буквы/цифры."""
    address = address.strip()
    return len(address) >= 10 and any(char.isalnum() for char in address)
