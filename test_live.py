from datetime import datetime
import board
import adafruit_dht

import dash
from dash import dcc, html
import plotly
from dash.dependencies import Input, Output

# pip install pyorbital

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Temperature sensor Feed'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=0
        )
    ])
)


#@app.callback(Output('live-update-text', 'children'),
#              Input('interval-component', 'n_intervals'))
#def update_metrics(n):
    #lon, lat, alt = satellite.get_lonlatalt(datetime.datetime.now())
#    style = {'padding': '5px', 'fontSize': '16px'}
    
#    time, temperature, humidity = get_sensor_reading()
#    return [
#        html.Span('Time: {}'.format(time), style=style),
#        html.Span('Temperature: {0:.2f}'.format(temperature), style=style),
#        html.Span('Humidity: {0:0.2f}'.format(humidity), style=style)
#    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    global sensor_data

    sensor_data.get_new_reading()

    fig = plotly.tools.make_subplots(rows=1, cols=1)

    fig.append_trace({
        "x": sensor_data.timestamps, 
        "y": sensor_data.temperature_datapoints,
        "name": "Bedroom temperature", 
        "type": "scatter"}, 1, 1)

    # # Set title
    fig.update_layout(
        title_text="Temperature over time",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
    )
    # Create the graph with subplots
#    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
#    fig['layout']['margin'] = {
#        'l': 30, 'r': 10, 'b': 30, 't': 10
#    }
#    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

#    fig.append_trace({
#        'x': data['time'],
#        'y': data['Altitude'],
#        'name': 'Altitude',
#        'mode': 'lines+markers',
#        'type': 'scatter'
#    }, 1, 1)
#    fig.append_trace({
#        'x': data['Longitude'],
#        'y': data['Latitude'],
#        'text': data['time'],
#        'name': 'Longitude vs Latitude',
#        'mode': 'lines+markers',
#        'type': 'scatter'
#    }, 2, 1)

    return fig

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

def get_sensor_reading():

    # Initial the dht device, with data pin connected to:
    dhtDevice = adafruit_dht.DHT22(board.D4)

    # you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
    # This may be necessary on a Linux single board computer like the Raspberry Pi,
    # but it will not work in CircuitPython.
    # dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

    # Print the values to the serial port


    temperature_c = dhtDevice.temperature
    temperature_f = temperature_c * (9 / 5) + 32

    humidity = dhtDevice.humidity

    now_time = datetime.now()

    str_info = "Time: {} Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
            now_time, temperature_f, temperature_c, humidity
        )
    print(str_info)
        
    dhtDevice.exit()

    return (now_time, temperature_c, humidity)

if __name__ == '__main__':

    global sensor_data
    sensor_data = DHTSensorData()

    app.run_server(debug=True, host='192.168.1.43')
