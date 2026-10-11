import logging
import random
import time

import requests

from .exceptions import ExternalServiceUnavailable

MAX_ATTEMPTS = 3
logger = logging.getLogger(__name__)


def get_json(url: str, params: dict | None = None) -> dict:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        delay = 2 ** (attempt - 1) + random.uniform(0, 0.5)

        try:
            response = requests.get(
                url=url,
                params=params,
                timeout=(3, 10),
            )

            if response.status_code >= 400:
                response.raise_for_status()

            if "application/json" not in response.headers.get("Content-Type", ""):
                logger.error(
                    "attempt %s/%s url=%s type=%s",
                    attempt,
                    MAX_ATTEMPTS,
                    url,
                    "ExternalServiceUnavailable",
                )
                raise ExternalServiceUnavailable("Ожидался JSON")
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as err:
                logger.error(
                    "attempt %s/%s url=%s type=%s",
                    attempt,
                    MAX_ATTEMPTS,
                    url,
                    "JSONDecodeError",
                )
                raise ExternalServiceUnavailable(f"Некорректный JSON: {err}")

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ):
            if attempt == MAX_ATTEMPTS:
                logger.error(
                    "attempt %s/%s url=%s type=%s",
                    attempt,
                    MAX_ATTEMPTS,
                    url,
                    "ExternalServiceUnavailable",
                )
                raise ExternalServiceUnavailable(
                    "Не удалось подключиться к серверу и получить ответ"
                )

            logger.warning(
                "retry %s/%s url=%s delay=%.1fs", attempt, MAX_ATTEMPTS, url, delay
            )
            time.sleep(delay)

        except requests.exceptions.HTTPError as err:
            status = err.response.status_code

            if status >= 500 and attempt < MAX_ATTEMPTS:
                logger.warning(
                    "retry %s/%s url=%s delay=%.1fs", attempt, MAX_ATTEMPTS, url, delay
                )
                time.sleep(delay)
                continue

            if status == 429 and attempt < MAX_ATTEMPTS:
                retry_after = err.response.headers.get("Retry-After")

                if retry_after and retry_after.isdigit():
                    delay = int(retry_after)
                    logger.warning(
                        "retry %s/%s url=%s delay=%.1fs",
                        attempt,
                        MAX_ATTEMPTS,
                        url,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                logger.warning(
                    "retry %s/%s url=%s delay=%.1fs", attempt, MAX_ATTEMPTS, url, delay
                )
                time.sleep(delay)
                continue

            logger.error(
                "attempt %s/%s url=%s type=%s",
                attempt,
                MAX_ATTEMPTS,
                url,
                "ExternalServiceUnavailable",
            )
            raise ExternalServiceUnavailable(str(err)) from err
