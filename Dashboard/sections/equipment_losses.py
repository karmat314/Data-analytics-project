import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go

# Load data
df = pd.read_csv('../Rus-Ukr-Equipment/ukr-rus-equipment_cleaned.csv')
df['Date'] = pd.to_datetime(df['Date'])

# Calculate smoothed ratio column with 7-day rolling average (centered)
df['Ratio_RU_UA_Smoothed'] = df['Ratio RU/UA'].rolling(window=7, center=True).mean()

equipment_layout = html.Div([
    html.H2("Equipment Destroyed Over Time"),
    
    dcc.Slider(
        id='date-slider',
        min=0,
        max=len(df) - 1,
        value=0,
        marks={i: df['Date'].dt.strftime('%Y-%m-%d').iloc[i] for i in range(0, len(df), max(1, len(df)//10))},
        step=1
    ),
    
    # Russia row
    html.Div([
        html.H3("Russia"),
        html.Div([
            html.Div([
                html.Img(src='/assets/tank.png', style={'width': '200px'}),
                html.H4(id='russia-tanks-destroyed')
            ], style={'display': 'inline-block', 'text-align': 'center', 'margin': '20px'}),
            
            html.Div([
                html.Img(src='/assets/aircraft.png', style={'width': '200px'}),
                html.H4(id='russia-aircraft-destroyed')
            ], style={'display': 'inline-block', 'text-align': 'center', 'margin': '20px'}),
            
            html.Div([
                html.Img(src='/assets/artillery.png', style={'width': '200px'}),
                html.H4(id='russia-artillery-destroyed')
            ], style={'display': 'inline-block', 'text-align': 'center', 'margin': '20px'}),
        ], style={'text-align': 'center'}),
        html.Div(id='russia-total-destroyed', style={'textAlign': 'center', 'fontSize': '20px', 'marginTop': '10px'}),
    ], style={'marginBottom': '40px'}),
    
    # Ukraine row
    html.Div([
        html.H3("Ukraine"),
        html.Div([
            html.Div([
                html.Img(src='/assets/tank.png', style={'width': '200px'}),
                html.H4(id='ukraine-tanks-destroyed')
            ], style={'display': 'inline-block', 'text-align': 'center', 'margin': '20px'}),
            
            html.Div([
                html.Img(src='/assets/aircraft.png', style={'width': '200px'}),
                html.H4(id='ukraine-aircraft-destroyed')
            ], style={'display': 'inline-block', 'text-align': 'center', 'margin': '20px'}),
            
            html.Div([
                html.Img(src='/assets/artillery.png', style={'width': '200px'}),
                html.H4(id='ukraine-artillery-destroyed')
            ], style={'display': 'inline-block', 'text-align': 'center', 'margin': '20px'}),
        ], style={'text-align': 'center'}),
        html.Div(id='ukraine-total-destroyed', style={'textAlign': 'center', 'fontSize': '20px', 'marginTop': '10px'}),
    ]),
    
    # Ratio plot
    html.Div([
        dcc.Graph(id='loss-ratio-graph')
    ], style={'marginTop': '50px'})
])

def register_callbacks(app):
    @app.callback(
        Output('russia-tanks-destroyed', 'children'),
        Output('russia-aircraft-destroyed', 'children'),
        Output('russia-artillery-destroyed', 'children'),
        Output('russia-total-destroyed', 'children'),
        Output('ukraine-tanks-destroyed', 'children'),
        Output('ukraine-aircraft-destroyed', 'children'),
        Output('ukraine-artillery-destroyed', 'children'),
        Output('ukraine-total-destroyed', 'children'),
        Input('date-slider', 'value')
    )
    def update_destroyed_numbers(selected_index):
        row = df.iloc[selected_index]
        
        # Russia
        r_tanks = int(row['Russia_Tanks'])
        r_aircraft = int(row['Russia_Aircraft'])
        r_artillery = int(row['Russia_Artillery'])
        r_total = r_tanks + r_aircraft + r_artillery
        
        # Ukraine
        u_tanks = int(row['Ukraine_Tanks'])
        u_aircraft = int(row['Ukraine_Aircraft'])
        u_artillery = int(row['Ukraine_Artillery'])
        u_total = u_tanks + u_aircraft + u_artillery
        
        return (
            f"Tanks Destroyed: {r_tanks}",
            f"Aircraft Destroyed: {r_aircraft}",
            f"Artillery Destroyed: {r_artillery}",
            f"Total Equipment Destroyed: {r_total}",
            f"Tanks Destroyed: {u_tanks}",
            f"Aircraft Destroyed: {u_aircraft}",
            f"Artillery Destroyed: {u_artillery}",
            f"Total Equipment Destroyed: {u_total}",
        )

    @app.callback(
        Output('loss-ratio-graph', 'figure'),
        Input('date-slider', 'value')  # Input here to trigger update if needed
    )
    def update_loss_ratio(_):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['Ratio_RU_UA_Smoothed'], 
            mode='lines', 
            name='Smoothed Ratio', 
            line=dict(color='purple')
        ))
        fig.add_hline(
            y=1, 
            line_dash='dash', 
            line_color='black', 
            annotation_text='1:1 Ratio', 
            annotation_position='top left'
        )
        fig.update_layout(
            title='Ratio of Russian to Ukrainian Equipment Losses Over Time (Smoothed)',
            xaxis_title='Date',
            yaxis_title='Loss Ratio',
            height=600,
            template='plotly_white',
            margin=dict(l=40, r=40, t=60, b=40)
        )
        return fig
