# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import csv

from datetime import datetime

import board
import adafruit_dht


def read_sensor():

    # Initial the dht device, with data pin connected to:
    dhtDevice = adafruit_dht.DHT22(board.D4)

    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

    while True:

        with open("temp_data_fri.csv", "a") as file:
            writer = csv.writer(file)

            try:
                # Print the values to the serial port
                
                temperature_c = dhtDevice.temperature
                temperature_f = temperature_c * (9 / 5) + 32
                
                humidity = dhtDevice.humidity
                
                now_time = datetime.now()
                
                str_info = "Time: {} Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                        now_time, temperature_f, temperature_c, humidity
                    )
                print(str_info)
                
                writer.writerow([now_time, temperature_c, humidity])

            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                print(error.args[0])
                time.sleep(2.0)
                continue
            except Exception as error:
                dhtDevice.exit()
                raise error

            time.sleep(600.0)


if __name__ == "__main__":

    # app.run(debug=True, port=5000, host='192.168.1.43')
    read_sensor()
