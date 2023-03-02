# Raspberry Pi Temperature Sensor plotting

Plotting and hosting webserver on raspberry pi with temperature and humidity sensor

![Example temperature plot](data/temp_plot.png)

Feature ideas:
- [X] Save sensor data from pi as csv
- [X] Write data to sqlite database
- [X] Plot csv data in Python
- [X] Host server on pi with API to get sensor updates
- [X] Separate backend data logging with frontend interval plotting
- [X] Plot sensor updates real-time with sever on pi - done using dash callback instead of flask API
- [X] Get outside temperature as data for plot
- [X] Access nest thermostat API and add to plot
- ~~Logic to optimise heating schedule~~
