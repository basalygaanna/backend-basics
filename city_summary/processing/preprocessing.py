weather_code_desc = {
    "0": "Clear sky",
    "1": "Mainly clear",
    "2": "Partly cloudy",
    "3": "Overcast",
    "45": "Fog",
    "48": "Depositing rime fog",
    "51": "Light drizzle",
    "53": "Moderate drizzle",
    "55": "Dense drizzle",
    "56": "Light freezing drizzle",
    "57": "Dense freezing drizzle",
    "61": "Slight rain",
    "63": "Moderate rain",
    "65": "Heavy rain",
    "66": "Light freezing rain",
    "67": "Heavy freezing rain",
    "71": "Slight snowfall",
    "73": "Moderate snowfall",
    "75": "Heavy snowfall",
    "77": "Snow grains",
    "80": "Slight rain showers",
    "81": "Moderate rain showers",
    "82": "Violent rain showers",
    "85": "Slight snow showers",
    "86": "Heavy snow showers",
    "95": "Thunderstorm",
    "96": "Thunderstorm with slight hail",
    "97": "Heavy thunderstorm",
    "99": "Thunderstorm with heavy hail"
}


def is_warm_clothes(temp):
    return temp < 0


def is_expensive(rate):
    return rate > 100


def text_description(desc_code):
    return weather_code_desc.get(str(desc_code), 'Unknown')


def take_umbrella(desc_code):
    return str(desc_code) in ['51', '53', '55', '56', '57', '61', '63', '65', '66',
                          '67', '80', '81', '82']


