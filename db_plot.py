from datetime import datetime
import sqlite3
import numpy as np

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

    def _get_db_data(self, db):
        # Connect to the database
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM data")

        # Fetch the results of the query
        results = cursor.fetchall()

        conn.commit()
        conn.close()

        return results

    def get_new_reading(self):
        bedroom_data = np.array(self._get_db_data(self.bedroom_db))
        self.fig["data"][0]["x"] = bedroom_data[:, 0]
        self.fig["data"][0]["y"] = bedroom_data[:, 1]

        livingroom_data = np.array(self._get_db_data(self.livingroom_db))
        self.fig["data"][1]["x"] = livingroom_data[:, 0]
        self.fig["data"][1]["y"] = livingroom_data[:, 1]

        external_data = np.array(self._get_db_data(self.external_db))
        self.fig["data"][2]["x"] = external_data[:, 0]
        self.fig["data"][2]["y"] = external_data[:, 1]

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
