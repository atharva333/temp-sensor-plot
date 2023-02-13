from datetime import datetime
import json
import sqlite3
import requests

from .sensor_db import BaseSensorDB


class ExternalTemperatureData:
    """
    Get external temperature data from public API
    """

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


class ExternalTemperatureDB(BaseSensorDB):
    """
    Get external temperature data from public API and save to DB
    """

    latitude = 55.9453
    longitude = -3.182

    def __init__(self):
        self.database_filepath = "data/external.db"
        self._create_db_table()

    def get_new_reading(self):
        # Connect to the database
        self.conn = sqlite3.connect(self.database_filepath)
        self.conn_cursor = self.conn.cursor()

        try:
            url = "https://api.open-meteo.com/v1/forecast"

            data = {"latitude": self.latitude, "longitude": self.longitude, "current_weather": True}

            timestamp = datetime.now()

            response = requests.get(url, data)

            temperature = response.json()["current_weather"]["temperature"]
            humidity = 0

            # Insert data into the table
            self.conn_cursor.execute(
                "INSERT INTO data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                (timestamp, temperature, humidity),
            )
            self.conn.commit()

            success = True

        except Exception as e:
            print(e)
            success = False

        self.conn.close()

        return success


if __name__ == "__main__":
    # Test sensor data
    import time

    dht_db = ExternalTemperatureDB()

    for i in range(10):
        print(i)
        dht_db.get_new_reading()
        time.sleep(0.1)
