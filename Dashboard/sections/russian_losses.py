from dash import html, dcc, Output, Input
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Data
officer_data = pd.DataFrame({
    "Rank": [
        "Junior Lieutenant", "Lieutenant", "Senior Lieutenant", "Captain", "Major",
        "Lieutenant Colonel", "Colonel", "Major General", "Lieutenant General",
        "Colonel General", "General of the Army", "Other Rank and Unknown Rank",
        "Reserve/Retired Junior Officer", "Reserve/Retired Senior Officer"
    ],
    "Count": [461, 1238, 1527, 941, 610, 290, 107, 7, 3, 0, 0, 171, 309, 347]
}).sort_values(by="Count", ascending=False)

df2 = pd.read_csv('../Russian soldier and civilian losses/Confirmed Russian losses in Ukraine per week.csv')
df2['week_start'] = pd.to_datetime(df2['week_start'], format='%d.%m.%Y')
df2_plot = df2.set_index('week_start')

# Officer deaths bar chart
fig_rank = px.bar(officer_data, x='Rank', y='Count', title='Russian Officers Killed by Rank',
                  labels={'Count': 'Number Killed'}, color='Count', color_continuous_scale='Reds')
fig_rank.update_layout(xaxis_tickangle=-45, margin=dict(l=40, r=20, t=50, b=100))

# Line chart: Total losses
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=df2['week_start'], y=df2['total'], mode='lines+markers', name='Total Losses'))
fig_line.update_layout(title='Russian Total Losses Over Time',
                       xaxis_title='Week Start', yaxis_title='Personnel Lost',
                       xaxis=dict(tickangle=45))




# Stacked bar chart: Breakdown
fig_stack = go.Figure()
fig_stack.add_trace(go.Bar(x=df2['week_start'], y=df2['vol'], name='Volunteers'))
fig_stack.add_trace(go.Bar(x=df2['week_start'], y=df2['mob'], name='Mobilized'))
fig_stack.add_trace(go.Bar(x=df2['week_start'], y=df2['inmates'], name='Inmates'))
fig_stack.update_layout(barmode='stack', title='Weekly Breakdown by Category',
                        xaxis_title='Week Start', yaxis_title='Personnel Lost',
                        xaxis=dict(tickangle=45))

html.Label('Select Time Aggregation:', style={'marginTop': '30px'}),
dcc.Dropdown(
    id='aggregation-dropdown',
    options=[
        {'label': 'Weekly', 'value': 'W'},
        {'label': 'Monthly', 'value': 'M'},
        {'label': 'Yearly', 'value': 'Y'}
    ],
    value='W',
    clearable=False,
    style={'width': '40%'}
),


russian_losses_layout = html.Div([
    html.H3('Russian Officer and Personnel Losses', style={'marginTop': '20px'}),
    dcc.Graph(figure=fig_rank),
    dcc.Graph(figure=fig_line, id='loss-graph', style={'height': '600px'}),
    dcc.Graph(figure=fig_stack, id='loss-graph-stack', style={'height': '600px'}),
])

# Callback
def register_callbacks(app):
    @app.callback(
        Output('loss-graph', 'figure'),
        Input('loss-view-dropdown', 'value')
    )
    def update_graph(view_choice):
        df_agg = df2.copy()
        df_agg = df_agg.resample(aggregation, on='week_start').sum(numeric_only=True).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_agg['week_start'], y=df_agg['vol'], name='Volunteers'))
        fig.add_trace(go.Bar(x=df_agg['week_start'], y=df_agg['mob'], name='Mobilized'))
        fig.add_trace(go.Bar(x=df_agg['week_start'], y=df_agg['inmates'], name='Inmates'))

        fig.update_layout(
        barmode='stack', title='Breakdown by Category',
        xaxis_title='Date', yaxis_title='Personnel Lost',
        xaxis=dict(tickangle=45)
        )
        return fig


