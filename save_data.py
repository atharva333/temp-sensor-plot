from datetime import datetime
import threading
import time
import json

from sensor_reading.sensor import DHTDB
from sensor_reading.nest import NestAPIDB
from sensor_reading.external import ExternalTemperatureDB

SAVE_INTERVAL = 120  # in seconds, time between getting new data


def main():
    pi_sensor = DHTDB()
    nest_sensor = NestAPIDB()
    external_sensor = ExternalTemperatureDB()

    while True:
        try:
            pi_start_time = time.perf_counter()
            pi_sensor.get_new_reading()
            print(f"Pi sensor time: {time.perf_counter() - pi_start_time}")

            nest_start_time = time.perf_counter()
            nest_sensor.get_new_reading()
            print(f"Nest sensor time: {time.perf_counter() - nest_start_time}")

            ext_start_time = time.perf_counter()
            external_sensor.get_new_reading()
            print(f"External sensor time: {time.perf_counter() - ext_start_time}")

            print(f"Sleep for {SAVE_INTERVAL - (ext_start_time - pi_start_time)}")
            print("")
            time.sleep(SAVE_INTERVAL - (ext_start_time - pi_start_time))

        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
