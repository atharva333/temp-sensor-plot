import json
import requests


class NestAPIData:
    """
    Class for getting Nest API data with methods for getting access token and updating data log
    """

    api_config_file = "api_token.json"

    def __init__(self):
        with open(self.api_config_file) as fileread:
            self.api_info = json.load(fileread)

        self.get_access_token()

        self.temperature_datapoints = []
        self.humidity_datapoints = []

    def get_access_token(self):
        print("Getting new access token")

        data = {
            "client_id": self.api_info["client_id"],
            "client_secret": self.api_info["client_secret"],
            "refresh_token": self.api_info["refresh_token"],
            "grant_type": "refresh_token",
        }
        url = "https://www.googleapis.com/oauth2/v4/token?"

        response = requests.post(url, data)

        self.access_token = response.json()["access_token"]

    def get_nest_sensor_data(self):
        try:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.access_token}"}

            url = "https://smartdevicemanagement.googleapis.com/v1/enterprises/3f7b67ed-ad48-43d0-b6cf-9b05132cee6b/devices"

            response = requests.get(url, headers=headers)

            temperature = response.json()["devices"][0]["traits"]["sdm.devices.traits.Temperature"][
                "ambientTemperatureCelsius"
            ]
            self.temperature_datapoints.append(temperature)

            humidity = response.json()["devices"][0]["traits"]["sdm.devices.traits.Humidity"]["ambientHumidityPercent"]
            self.humidity_datapoints.append(humidity)

            print(temperature, humidity)
            return True

        except KeyError as e:
            print(e)
            self.get_access_token()

            return False
