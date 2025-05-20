import pandas as pd
from dash import html, dcc, Input, Output

# Load data here or pass it from the main app
df = pd.read_csv('../Rus-Ukr-Equipment/ukr-rus-equipment_cleaned.csv')
df['Date'] = pd.to_datetime(df['Date'])


equipment_layout = html.Div([
    html.H2("Equipment Destroyed Over Time"),
    
    dcc.Slider(
        id='date-slider',
        min=0,
        max=len(df) - 1,
        value=0,
        marks = {i: df['Date'].dt.strftime('%Y-%m-%d').iloc[i] for i in range(0, len(df), max(1, len(df)//10))},
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
