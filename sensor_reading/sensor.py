from datetime import datetime
import board
import adafruit_dht
import sqlite3
import time

from .sensor_db import BaseSensorDB


class DHTSensorData:
    """
    Read from GPIO data with specific library for DHT22 temperature and humidity sensor
    """

    def __init__(self) -> None:
        # Initialise data structure for storing DHT temperature sensor data

        self.timestamps = []
        self.temperature_datapoints = []
        self.humidity_datapoints = []

        # Initial the dht device, with data pin connected to:
        self.dhtDevice = adafruit_dht.DHT22(board.D4)

    def get_new_reading(self) -> None:
        """Get new reading from sensor"""

        while True:
            try:
                # Get timestamp and readings
                timestamp = datetime.now()
                temperature_reading = self.dhtDevice.temperature
                humidity_reading = self.dhtDevice.humidity

                str_info = f"Time: {timestamp} Temp: {temperature_reading:.1f} C    Humidity: {humidity_reading}% "
                print(str_info)

                # Append to list
                self.timestamps.append(timestamp)
                self.temperature_datapoints.append(temperature_reading)
                self.humidity_datapoints.append(humidity_reading)

                break

            except RuntimeError as e:
                print(e)
                continue

            except Exception as e:
                print(e)

        self.dhtDevice.exit()
        return None


class DHTDB(BaseSensorDB):
    def __init__(self):
        # Set db filepath
        self.database_filepath = "data/dht.db"
        self._create_db_table()

        # Initial the dht device, with data pin connected to:
        self.dhtDevice = adafruit_dht.DHT22(board.D4)

    def get_new_reading(self) -> bool:
        """Get new reading from sensor"""

        # Connect to the database
        self.conn = sqlite3.connect(self.database_filepath)
        self.conn_cursor = self.conn.cursor()

        while True:
            try:
                # Get timestamp and readings
                timestamp = datetime.now()
                temperature_reading = self.dhtDevice.temperature
                humidity_reading = self.dhtDevice.humidity

                str_info = f"Time: {timestamp} Temp: {temperature_reading:.1f} C    Humidity: {humidity_reading}% "
                print(str_info)

                # Insert data into the table
                self.conn_cursor.execute(
                    "INSERT INTO data (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                    (timestamp, temperature_reading, humidity_reading),
                )
                self.conn.commit()

                success = True
                break

            except RuntimeError as e:
                print(e)
                continue

            except Exception as e:
                print(e)
                success = False

        ## Cleanup
        # Close GPIO connection
        self.dhtDevice.exit()

        # Close connection to db
        self.conn.close()

        return success


if __name__ == "__main__":
    # Test sensor data

    dht_db = DHTDB()

    for i in range(10):
        print(i)
        dht_db.get_new_reading()
        time.sleep(0.1)
