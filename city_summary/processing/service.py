from clients.rates import get_rate
from clients.weather import get_weather

from .preprocessing import (
    is_expensive,
    is_warm_clothes,
    take_umbrella,
    text_description,
)


def build_city_summary(city, currency="USD") -> dict:
    weather = get_weather(city)
    rate = get_rate(currency)

    return {
        "city": city,
        "weather": {
            "temp_c": weather["temp_c"],
            "description": text_description(weather["description_code"]),
            "warm_clothes": is_warm_clothes(weather["temp_c"]),
            "umbrella": take_umbrella(weather["description_code"]),
        },
        "rates": {
            "currency": currency,
            "rate_to_rub": rate,
            "expensive": is_expensive(rate),
        },
    }
