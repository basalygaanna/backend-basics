import logging
import time

from .exceptions import CurrencyNotFound, ExternalServiceUnavailable
from .http import get_json

INTERVAL = 300

logger = logging.getLogger(__name__)
cache: dict[str, tuple[float, float]] = {}


def get_rate(currency: str) -> float:
    cur_sec = time.monotonic()

    if cache.get(currency) and cur_sec - cache[currency][1] < INTERVAL:
        logger.info("currency=%s was taken from cache", currency)
        return cache[currency][0]

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
            "url=%s currency=%s type=%s", url_rates, currency, "CurrencyNotFound"
        )
        raise CurrencyNotFound("Код валюты не найден")

    cache[currency] = (rate["rate"], cur_sec)
    logger.info("currency=%s was taken from api", currency)
    return rate["rate"]
