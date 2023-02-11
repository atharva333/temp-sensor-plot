import plotly.graph_objects as go
from datetime import datetime
import pandas as pd


if __name__ == "__main__":

    # Load data
    df = pd.read_csv(
        "/home/atharva/Desktop/Python/temp_data_fri.csv")

    print(df.dtypes)

    # Create figure
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(x=list(df.datetime), y=list(df.temperature)))

    # # Set title
    fig.update_layout(
        title_text="Temperature over time",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
    )

    fig.add_vline(x=datetime(2023, 2, 11, 5, 30, 0, 0).timestamp()*1000, line_dash="dot",
              annotation_text="Heating turned on", 
              annotation_position="top right")

    # # Add range slider
    # fig.update_layout(
    #     xaxis=dict(
    #         rangeselector=dict(
    #             buttons=list([
    #                 dict(count=1,
    #                     label="1m",
    #                     step="month",
    #                     stepmode="backward"),
    #                 dict(count=6,
    #                     label="6m",
    #                     step="month",
    #                     stepmode="backward"),
    #                 dict(count=1,
    #                     label="YTD",
    #                     step="year",
    #                     stepmode="todate"),
    #                 dict(count=1,
    #                     label="1y",
    #                     step="year",
    #                     stepmode="backward"),
    #                 dict(step="all")
    #             ])
    #         ),
    #         rangeslider=dict(
    #             visible=True
    #         ),
    #         type="date"
    #     )
    # )

    fig.show()

    print("test")