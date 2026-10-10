import argparse
import sys

from clients.exceptions import (
    CityNotFound,
    CurrencyNotFound,
    ExternalServiceUnavailable,
)
from processing.service import build_city_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True)
    parser.add_argument("--currency", default="USD")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        summary = build_city_summary(args.city, args.currency)
    except (CityNotFound, CurrencyNotFound) as err:
        print(str(err))
        return 3
    except ExternalServiceUnavailable as err:
        print(str(err))
        return 4

    print(f'Город: {summary["city"]}')
    print(
        f'Погода: {summary["weather"]["temp_c"]}°C, {summary["weather"]["description"]}')
    print(
        f'Теплая одежда: {"да" if summary["weather"]["warm_clothes"] else "нет"}')
    print(f'Нужен зонт: {"да" if summary["weather"]["umbrella"] else "нет"}')
    print(
        f'{summary["rates"]["currency"]}->RUB: {summary["rates"]["rate_to_rub"]}')
    print(f'Дорогой курс: {"да" if summary["rates"]["expensive"] else "нет"}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
