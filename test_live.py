from datetime import datetime
import csv

import dash
from dash import dcc, html
import plotly
from dash.dependencies import Input, Output

from sensor_reading.sensor import DHTSensorData
from sensor_reading.nest import NestAPIData
from sensor_reading.external import ExternalTemperatureData


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

        self.fig.append_trace({"x": [], "y": [], "name": "Bedroom", "type": "scatter", "mode": "markers"}, 1, 1)

        self.fig.append_trace({"x": [], "y": [], "name": "Living room", "type": "scatter", "mode": "markers"}, 1, 1)

        self.fig.append_trace({"x": [], "y": [], "name": "Outside", "type": "scatter", "mode": "markers"}, 1, 1)

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
