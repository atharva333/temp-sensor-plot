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
            interval=5*1000, # in milliseconds
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
#    satellite = Orbital('TERRA')
    #time, temperature, humidity = get_sensor_reading()

    global data

    # Collect some data
#    for i in range(180):
#        time = datetime.datetime.now() - datetime.timedelta(seconds=i*20)
#        lon, lat, alt = satellite.get_lonlatalt(
#            time
#        )
#        data['Longitude'].append(lon)
#        data['Latitude'].append(lat)
#        data['Altitude'].append(alt)
#        data['time'].append(time)
    time, temperature, humidity = get_sensor_reading()
    data["time"].append(time)
    data["temperature"].append(temperature)

    fig = plotly.tools.make_subplots(rows=1, cols=1)

    fig.append_trace({
        "x": data["time"], 
        "y": data["temperature"], 
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
    
    global data
    data = {
        'time': [],
        'temperature': [],
        'humidity': [],
    }

    app.run_server(debug=True, host='192.168.1.43')
