from .http import get_json
from .exceptions import CurrencyNotFound, ExternalServiceUnavailable


def get_rate(currency) -> float:
    url_rates = f'https://api.frankfurter.dev/v2/rate/{currency}/RUB'
    try:
        rate = get_json(url_rates)
    except ExternalServiceUnavailable as err:
        if "404" in str(err) or "422" in str(err):
            raise CurrencyNotFound("Валюта не найдена")
        raise

    if not rate:
        raise CurrencyNotFound("Валюта не найдена")
    return rate.get('rate')
