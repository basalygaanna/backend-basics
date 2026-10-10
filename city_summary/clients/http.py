import time, requests, random
from .exceptions import ExternalServiceUnavailable

MAX_ATTEMPTS = 3


def get_json(url, params=None):
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

            if "application/json" not in response.headers.get("Content-Type",
                                                              ""):
                raise ExternalServiceUnavailable("Ожидался JSON")
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as err:
                raise ExternalServiceUnavailable(f"Некорректный JSON: {err}")

        except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
        ):
            if attempt == MAX_ATTEMPTS:
                raise ExternalServiceUnavailable("Не удалось подключиться к серверу и получить ответ")

            time.sleep(delay)

        except requests.exceptions.HTTPError as err:
            status = err.response.status_code

            if status >= 500 and attempt < MAX_ATTEMPTS:
                time.sleep(delay)
                continue

            if status == 429 and attempt < MAX_ATTEMPTS:
                retry_after = err.response.headers.get("Retry-After")

                if retry_after and retry_after.isdigit():
                    delay = int(retry_after)
                    time.sleep(delay)
                    continue

                time.sleep(delay)
                continue

            raise ExternalServiceUnavailable(str(err)) from err
