class CityNotFound(Exception):
    """Город не найден в геокодере."""


class CurrencyNotFound(Exception):
    """Код валюты не найден."""


class ExternalServiceUnavailable(Exception):
    """Внешний сервис недоступен после всех retry."""
