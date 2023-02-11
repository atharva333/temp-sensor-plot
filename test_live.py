from datetime import datetime
import board
import adafruit_dht

import requests
import json

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

class NestAPIData:

    api_config_file = "api_token.json"

    def __init__(self):

        with open(self.api_config_file) as fileread:
            self.api_info = json.load(fileread)

        self.access_token = self.get_access_token()

        self.temperature_datapoints = []
        self.humidity_datapoints = []

    def get_access_token(self):
        data = {
            "client_id": self.api_info["client_id"],
            "client_secret": self.api_info["client_secret"],
            "refresh_token": self.api_info["refresh_token"],
            "grant_type":"refresh_token",
            }
        url = "https://www.googleapis.com/oauth2/v4/token?"

        response = requests.post(url, data)

        return response.json()["access_token"]

    def get_nest_sensor_data(self):

        headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {self.access_token}"}

        url = "https://smartdevicemanagement.googleapis.com/v1/enterprises/3f7b67ed-ad48-43d0-b6cf-9b05132cee6b/devices"

        response = requests.get(url, headers=headers)

        temperature = response.json()["devices"][0]["traits"]["sdm.devices.traits.Temperature"]["ambientTemperatureCelsius"]
        self.temperature_datapoints.append(temperature)

        humidity = response.json()["devices"][0]["traits"]["sdm.devices.traits.Humidity"]["ambientHumidityPercent"]
        self.humidity_datapoints.append(humidity)

        print(temperature, humidity)


class PlotlyLiveServer:

    def __init__(self):
        """Initialise sensor and graph figure data"""
        self.sensor_data = DHTSensorData()

        self.nest_data = NestAPIData()
        
        self.fig = plotly.tools.make_subplots(rows=1, cols=1)
        self.fig.update_layout(
            title_text="Temperature over time",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
        )

        self.fig.append_trace({
            "x": [], 
            "y": [],
            "name": "Bedroom", 
            "type": "scatter",
            "mode": "markers"}, 1, 1)

        self.fig.append_trace({
            "x": [], 
            "y": [],
            "name": "Living room", 
            "type": "scatter",
            "mode": "markers"}, 1, 1)

        self.fig.update_layout(legend_title_text="Location", showlegend=True)

    def get_new_reading(self):

        self.sensor_data.get_new_reading()
        self.nest_data.get_nest_sensor_data()

        self.fig["data"][0]["x"] = self.sensor_data.timestamps
        self.fig["data"][0]["y"] = self.sensor_data.temperature_datapoints

        self.fig["data"][1]["x"] = self.sensor_data.timestamps # Use same timestamp as sensor data
        self.fig["data"][1]["y"] = self.nest_data.temperature_datapoints

        return self.fig


if __name__ == '__main__':

    server = PlotlyLiveServer()

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(
        html.Div([
            html.H4('Temperature sensor Feed'),
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=30*1000, # in milliseconds
                n_intervals=0
            )
        ])
    )

    # Multiple components can update everytime interval gets fired.
    @app.callback(Output('live-update-graph', 'figure'),
                Input('interval-component', 'n_intervals'))
    def update_graph_live(n):
        return server.get_new_reading()

    app.run_server(debug=True, host='192.168.1.43')
