from datetime import datetime, date, timedelta
import sqlite3
import numpy as np

import time
import dash

from dash import dcc, html
import plotly
from dash.dependencies import Input, Output


class PlotlyLiveServer:
    def __init__(self):
        """Initialise sensor and graph figure data"""

        self.bedroom_db = "data/dht.db"
        self.livingroom_db = "data/nest.db"
        self.external_db = "data/external.db"

        self._set_up_figure()

    def _set_up_figure(self):
        self.fig = plotly.tools.make_subplots(rows=1, cols=1)
        self.fig.update_layout(
            title_text="Temperature over time",
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            yaxis_range=[-5, 25],
        )

        self.fig.append_trace(
            {
                "x": [],
                "y": [],
                "name": "Bedroom",
                "type": "scatter",
                "mode": "lines+markers",
                "marker": {
                    "size": 3,
                    "symbol": "circle",
                },
            },
            1,
            1,
        )

        self.fig.append_trace(
            {
                "x": [],
                "y": [],
                "name": "Living room",
                "type": "scatter",
                "mode": "lines+markers",
                "marker": {
                    "size": 3,
                    "symbol": "circle",
                    "color": "royalblue",
                },
            },
            1,
            1,
        )

        self.fig.append_trace(
            {
                "x": [],
                "y": [],
                "name": "Outside",
                "type": "scatter",
                "mode": "lines+markers",
                "marker": {
                    "size": 3,
                    "symbol": "circle",
                },
            },
            1,
            1,
        )

        self.fig.update_layout(legend_title_text="Location", showlegend=True, template="ggplot2")

    def _get_db_data(self, db, start_date=None, end_date=None):
        # Connect to the database
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        if (start_date is not None) and (end_date is not None):
            print("Time")
            cursor.execute(f"SELECT * FROM data WHERE timestamp BETWEEN ? AND ?", (start_date, end_date))
        else:
            cursor.execute("SELECT * FROM data ORDER BY timestamp DESC LIMIT 1")

        # Fetch the results of the query
        results = cursor.fetchall()

        # print(results)

        conn.commit()
        conn.close()

        return results

    def get_updated_figure(self, start_date=None, end_date=None):
        bedroom_data = self._get_db_data(self.bedroom_db, start_date, end_date)
        self.fig["data"][0]["x"] = [row[0] for row in bedroom_data]
        self.fig["data"][0]["y"] = [row[1] for row in bedroom_data]

        livingroom_data = self._get_db_data(self.livingroom_db, start_date, end_date)
        self.fig["data"][1]["x"] = [row[0] for row in livingroom_data]
        self.fig["data"][1]["y"] = [row[1] for row in livingroom_data]

        external_data = self._get_db_data(self.external_db, start_date, end_date)
        self.fig["data"][2]["x"] = [row[0] for row in external_data]
        self.fig["data"][2]["y"] = [row[1] for row in external_data]

        return self.fig

    def get_latest_reading(self):
        readings = []
        readings.append(self._get_db_data(self.bedroom_db))
        readings.append(self._get_db_data(self.livingroom_db))
        readings.append(self._get_db_data(self.external_db))

        return readings


if __name__ == "__main__":
    server = PlotlyLiveServer()
    time.sleep(0.2)

    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    def serve_layout():
        """
        Function that is called during reload
        Allows shifting date picker and graph range based on page reload instead of server side date
        """
        return html.Div(
            html.Div(
                [
                    html.H4("Temperature sensor Feed"),
                    html.H5(id="current-temperature"),
                    html.Br(),
                    dcc.DatePickerRange(
                        id="my-date-picker-range",
                        min_date_allowed=date(2023, 2, 10),
                        max_date_allowed=date(2023, 12, 31),
                        initial_visible_month=datetime.today(),
                        start_date=(datetime.today() - timedelta(days=1)).date(),
                        end_date=(datetime.today() + timedelta(days=1)).date(),
                    ),
                    dcc.Interval(id="interval-component", interval=120 * 1000, n_intervals=0),  # in milliseconds
                    dcc.Graph(id="live-update-graph"),
                ],
            )
        )

    # Multiple components can update everytime interval gets fired.
    @app.callback(Output("current-temperature", "children"), Input("interval-component", "n_intervals"))
    def update_graph_live(n):
        """
        Get latest reading from database for each data source / table
        """
        readings_list = server.get_latest_reading()
        return f"Current temperatures: Bedroom {readings_list[0][0][1]:.1f} | Living room {readings_list[1][0][1]:.1f} | Outside {readings_list[2][0][1]:.1f}"

    @app.callback(
        Output("live-update-graph", "figure"),
        [
            Input("my-date-picker-range", "start_date"),
            Input("my-date-picker-range", "end_date"),
        ],
    )
    def update_output(start_date, end_date):
        """
        Updates graph figure object based on start and end date from Dash's date picker component

        Args:
            start_date (string): Get start date as string from dash date picker
            end_date (string): Get end date as string from dash date picker

        Returns:
            fig: Updated figure as expected for dash graph component
        """
        try:
            string_prefix = "You have selected: "
            if start_date is not None:
                start_date_object = datetime.strptime(start_date, "%Y-%m-%d").date()

            if end_date is not None:
                end_date_object = datetime.strptime(end_date, "%Y-%m-%d").date()

            if (start_date is not None) and (end_date is not None):
                return server.get_updated_figure(start_date_object, end_date_object)
            else:
                return server.get_updated_figure()
        except Exception as e:
            print(e)
            raise e

    app.layout = serve_layout

    app.run_server(debug=True, host="192.168.1.43")
