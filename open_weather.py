import requests
import json
import time


def get_hourly_weather_data(API_KEY):
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat=12.985800&lon=77.529560&exclude=current,minutely,daily,alerts&units=metric&appid={API_KEY}"

    response = requests.get(url)
    for i in range(1, 2):
        temperature = response.json()["hourly"][i]["temp"]
        return temperature
