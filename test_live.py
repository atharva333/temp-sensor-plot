from datetime import datetime
import board
import adafruit_dht

import requests
import json
import csv

import dash
from dash import dcc, html
import plotly
from dash.dependencies import Input, Output


class DHTSensorData:
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

                str_info = (
                    f"Time: {timestamp} Temp: {temperature_reading:.1f} C    Humidity: {humidity_reading}% "
                )
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


class NestAPIData:
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

            humidity = response.json()["devices"][0]["traits"]["sdm.devices.traits.Humidity"][
                "ambientHumidityPercent"
            ]
            self.humidity_datapoints.append(humidity)

            print(temperature, humidity)
            return True

        except KeyError as e:
            print(e)
            self.get_access_token()

            return False


class ExternalTemperatureData:
    def __init__(self):
        self.temperature_datapoints = []
        self.humidity_datapoints = []

    def get_new_external_reading(self):
        try:
            url = "https://api.open-meteo.com/v1/forecast"

            data = {"latitude": 55.9453, "longitude": -3.182, "current_weather": True}

            response = requests.get(url, data)

            temperature = response.json()["current_weather"]["temperature"]
            self.temperature_datapoints.append(temperature)

            return True

        except Exception as e:
            print(e)
            return False


class PlotlyLiveServer:
    def __init__(self):
        """Initialise sensor and graph figure data"""
        self.sensor_data = DHTSensorData()

        self.nest_data = NestAPIData()

        self.outside_data = ExternalTemperatureData()

        start_time = datetime.now()
        self.csv_file_path = f"data/tempdata-{start_time.date()}-{start_time.time()}.csv"

        csv_file = open(self.csv_file_path, "a")
        headers = [
            "datetime",
            "bedroom_temperature",
            "bedroom_humidity",
            "livingroom_temperature",
            "livingroom_humidity",
            "outside_temperature",
            "outside_humidity",
        ]

        self.csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
        self.csv_writer.writeheader()
        csv_file.close()

        self.fig = plotly.tools.make_subplots(rows=1, cols=1)
        self.fig.update_layout(
            title_text="Temperature over time",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
        )

        self.fig.append_trace(
            {"x": [], "y": [], "name": "Bedroom", "type": "scatter", "mode": "markers"}, 1, 1
        )

        self.fig.append_trace(
            {"x": [], "y": [], "name": "Living room", "type": "scatter", "mode": "markers"}, 1, 1
        )

        self.fig.append_trace(
            {"x": [], "y": [], "name": "Outside", "type": "scatter", "mode": "markers"}, 1, 1
        )

        self.fig.update_layout(legend_title_text="Location", showlegend=True)

    def get_new_reading(self):
        csv_row = {
            "datetime": None,
            "bedroom_temperature": None,
            "bedroom_humidity": None,
            "livingroom_temperature": None,
            "livingroom_humidity": None,
            "outside_temperature": None,
            "outside_humidity": None,
        }

        self.sensor_data.get_new_reading()

        self.fig["data"][0]["x"] = self.sensor_data.timestamps
        self.fig["data"][0]["y"] = self.sensor_data.temperature_datapoints

        csv_row["datetime"] = self.sensor_data.timestamps[-1]
        csv_row["bedroom_temperature"] = self.sensor_data.temperature_datapoints[-1]
        csv_row["bedroom_humidity"] = self.sensor_data.humidity_datapoints[-1]

        if self.nest_data.get_nest_sensor_data():
            self.fig["data"][1]["x"] = self.sensor_data.timestamps  # Use same timestamp as sensor data
            self.fig["data"][1]["y"] = self.nest_data.temperature_datapoints

            csv_row["livingroom_temperature"] = self.nest_data.temperature_datapoints[-1]
            csv_row["livingroom_humidity"] = self.nest_data.humidity_datapoints[-1]

        if self.outside_data.get_new_external_reading():
            self.fig["data"][2]["x"] = self.sensor_data.timestamps  # Use same timestamp as sensor data
            self.fig["data"][2]["y"] = self.outside_data.temperature_datapoints

            csv_row["outside_temperature"] = self.outside_data.temperature_datapoints[-1]

        csv_file = open(self.csv_file_path, "a")
        self.csv_writer = csv.DictWriter(csv_file, csv_row.keys())
        self.csv_writer.writerow(csv_row)
        csv_file.close()

        return self.fig


if __name__ == "__main__":
    server = PlotlyLiveServer()

    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(
        html.Div(
            [
                html.H4("Temperature sensor Feed"),
                dcc.Graph(id="live-update-graph"),
                dcc.Interval(id="interval-component", interval=120 * 1000, n_intervals=0),  # in milliseconds
            ]
        )
    )

    # Multiple components can update everytime interval gets fired.
    @app.callback(Output("live-update-graph", "figure"), Input("interval-component", "n_intervals"))
    def update_graph_live(n):
        return server.get_new_reading()

    app.run_server(debug=True, host="192.168.1.43")
