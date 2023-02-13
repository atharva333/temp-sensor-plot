import json
import requests


class ExternalTemperatureData:
    latitude = 55.9453
    longitude = -3.182

    def __init__(self):
        self.temperature_datapoints = []
        self.humidity_datapoints = []

    def get_new_external_reading(self):
        try:
            url = "https://api.open-meteo.com/v1/forecast"

            data = {"latitude": self.latitude, "longitude": self.longitude, "current_weather": True}

            response = requests.get(url, data)

            temperature = response.json()["current_weather"]["temperature"]
            self.temperature_datapoints.append(temperature)

            return True

        except Exception as e:
            print(e)
            return False
