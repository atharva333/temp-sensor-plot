from datetime import datetime
import json
import requests
import sqlite3

from .sensor_db import BaseSensorDB


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
        print(response.json())

        self.access_token = response.json()["access_token"]

    def get_nest_sensor_data(self):
        try:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.access_token}"}

            url = "https://smartdevicemanagement.googleapis.com/v1/enterprises/3f7b67ed-ad48-43d0-b6cf-9b05132cee6b/devices"

            response = requests.get(url, headers=headers)
            print(json.dumps(response.json(), indent=2))

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

            self.temperature_datapoints.append(None)

            return False


class NestAPIDB(BaseSensorDB):
    """
    Class for getting Nest API data and adding to db
    """

    api_config_file = "api_token.json"

    def __init__(self):
        with open(self.api_config_file) as fileread:
            self.api_info = json.load(fileread)

        self.database_filepath = "data/nest.db"
        self._create_db_table()

        self.get_access_token()

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
        print(response.json())

        self.access_token = response.json()["access_token"]

    def get_new_reading(self) -> bool:
        # Connect to the database
        self.conn = sqlite3.connect(self.database_filepath)
        self.conn_cursor = self.conn.cursor()

        try:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.access_token}"}

            url = "https://smartdevicemanagement.googleapis.com/v1/enterprises/3f7b67ed-ad48-43d0-b6cf-9b05132cee6b/devices"

            timestamp = datetime.now()

            response = requests.get(url, headers=headers)
            # print(json.dumps(response.json(), indent=2))

            temperature = response.json()["devices"][0]["traits"]["sdm.devices.traits.Temperature"][
                "ambientTemperatureCelsius"
            ]

            humidity = response.json()["devices"][0]["traits"]["sdm.devices.traits.Humidity"]["ambientHumidityPercent"]

            print(f"Nest: timestamp {timestamp} temp {temperature}, humidity {humidity}")

            # Insert data into the table
            self.conn_cursor.execute(
                "INSERT INTO data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                (timestamp, temperature, humidity),
            )
            self.conn.commit()

            success = True

        except KeyError as e:
            print(e)
            self.get_access_token()

            success = False

        # Close connection to db
        self.conn.close()

        return success


if __name__ == "__main__":
    # Test sensor data
    import time

    dht_db = NestAPIDB()

    for i in range(10):
        print(i)
        dht_db.get_new_reading()
        time.sleep(0.1)
