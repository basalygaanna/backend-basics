import logging

from .exceptions import CityNotFound
from .http import get_json

URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
URL_FORECAST = "https://api.open-meteo.com/v1/forecast"

logger = logging.getLogger(__name__)


def get_weather(city: str) -> dict:
    coordinates = get_json(URL_GEOCODING, {"name": city, "count": 1})
    if not coordinates.get("results"):
        logger.error("url=%s city=%s type=%s", URL_GEOCODING, city, "CityNotFound")
        raise CityNotFound("Город не найден")
    lat = coordinates["results"][0]["latitude"]
    lon = coordinates["results"][0]["longitude"]

    weather = get_json(
        URL_FORECAST,
        {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "timezone": "Europe/Moscow",
        },
    )
    if not weather.get("current"):
        logger.warning("url=%s", URL_GEOCODING)
        logger.error("url=%s city=%s type=%s", URL_GEOCODING, city, "CityNotFound")
        raise CityNotFound("Город не найден")

    results = {
        "city": city,
        "temp_c": weather.get("current")["temperature_2m"],
        "description_code": weather.get("current")["weather_code"],
    }

    return results
