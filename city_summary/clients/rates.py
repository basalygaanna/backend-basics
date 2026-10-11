import logging

from .exceptions import CurrencyNotFound, ExternalServiceUnavailable
from .http import get_json

logger = logging.getLogger(__name__)


def get_rate(currency) -> float:
    url_rates = f"https://api.frankfurter.dev/v2/rate/{currency}/RUB"
    try:
        rate = get_json(url_rates)
    except ExternalServiceUnavailable as err:
        if "404" in str(err) or "422" in str(err):
            logger.error(
                "error code=%s url=%s currency=%s type=%s",
                str(err),
                url_rates,
                currency,
                "CurrencyNotFound",
            )
            raise CurrencyNotFound("Валюта не найдена")
        raise

    if not rate:
        logger.error(
            "url=%s currency=%s type=%s", url_rates, currency,
            "CurrencyNotFound"
        )
        raise CurrencyNotFound("Код валюты не найден")
    return rate.get("rate")
