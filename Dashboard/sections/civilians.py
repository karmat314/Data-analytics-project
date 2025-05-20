import json
import pandas as pd
import plotly.express as px
from dash import html, dcc

# Load preprocessed civilian data
df_ukr = pd.read_csv('../Rus-Ukr-Civilians/ukraine-civilian-preprocessed.csv')
df_rus = pd.read_csv('../Rus-Ukr-Civilians/russia-civilian-preprocessed.csv')


# Compute average fatalities per day for Ukraine
# Group by Area and aggregate total fatalities and total duration
area_avg = df_ukr.groupby('Area').agg({
    'Fatalities': 'sum',
    'Duration_Days': 'sum'
}).reset_index()

# Compute average fatalities per day
area_avg['Fatalities_Per_Day'] = area_avg['Fatalities'] / area_avg['Duration_Days']

# Sort to see highest averages
area_avg = area_avg.sort_values(by='Fatalities_Per_Day', ascending=False)


# Define layout for civilian fatality visualizations
civilians_layout = html.Div([
    html.H2("Civilian Fatalities Overview", style={"textAlign": "center"}),

    html.Div([
        html.H3("Ukraine: Fatalities by Area"),
        dcc.Graph(
            figure=px.bar(
                df_ukr,
                x='Area',
                y='Fatalities',
                title='Ukraine: Fatalities by Area',
                labels={'Fatalities': 'Fatalities', 'Area': 'Region'},
                color_discrete_sequence=['crimson']
            ).update_layout(xaxis_tickangle=-45)
        )
    ], style={"marginBottom": "50px"}),

    html.Div([
        html.H3("Russia: Fatalities by Area"),
        dcc.Graph(
            figure=px.bar(
                df_rus,
                x='Area',
                y='Fatalities',
                title='Russia: Fatalities by Area',
                labels={'Fatalities': 'Fatalities', 'Area': 'Region'},
                color_discrete_sequence=['darkblue']
            ).update_layout(xaxis_tickangle=-45)
        )
    ], style={"marginBottom": "50px"}),

    html.Div([
        html.H3("Ukraine: Average Fatalities per Day by Area"),
        dcc.Graph(
            figure=px.bar(
                area_avg,
                x='Area',
                y='Fatalities_Per_Day',
                title='Ukraine: Average Fatalities per Day by Area',
                labels={'Fatalities_Per_Day': 'Avg Fatalities/Day', 'Area': 'Region'},
                color_discrete_sequence=['darkred']
            ).update_layout(xaxis_tickangle=-45)
        )
    ])
], style={"padding": "20px"})
