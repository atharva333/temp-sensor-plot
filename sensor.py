from datetime import datetime
import board
import adafruit_dht

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