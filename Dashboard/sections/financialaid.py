# sections/financial_aid.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, callback
from plotly.subplots import make_subplots

# --- Load and Clean Dataset ---
df = pd.read_csv('../Financial-aid/financialaid.csv')

money_columns = [
    'tot_activity_value', 'tot_activity_value_EUR', 'tot_activity_value_constant_currency',
    'tot_sub_activity_value', 'tot_sub_activity_value_EUR', 'tot_sub_activity_value_constant_currency',
    'tot_sub_activity_value_constant_currency_redistr', 'tot_sub_activity_value_EUR_redistr',
    'tot_value_deliv_EUR', 'tot_sub_activity_value_EUR_OLD',
    'item_price_USD', 'item_value_estimate_USD', 'item_value_estimate_deliv_USD'
]

for col in money_columns:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(',', '').str.strip()
        df[col] = df[col].replace(['.', '', 'nan', 'NaN'], pd.NA)
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['announcement_date'] = pd.to_datetime(df['announcement_date'], errors='coerce')
df = df.dropna(subset=['donor', 'tot_activity_value_EUR', 'announcement_date'])

df['aid_type_general'] = df['aid_type_general'].astype(str).str.strip().str.title().replace(['Nan', ''], pd.NA)

df['donor'] = df['donor'].astype('category')
df['aid_type_general'] = df['aid_type_general'].astype('category')
df['year_month'] = df['announcement_date'].dt.to_period('M').astype(str)
df['month'] = df['announcement_date'].dt.month_name()
df['year'] = df['announcement_date'].dt.year

# --- 1. Aid by Donor Dropdown UI ---
aid_by_donor_ui = html.Div([
    html.H3("Aid by Donor"),
    dcc.Dropdown(
        id='donor-sort-dropdown',
        options=[
            {'label': 'Top 10 Donors (Highest Aid)', 'value': 'top'},
            {'label': 'Bottom 10 Donors (Lowest Aid)', 'value': 'bottom'}
        ],
        value='top',
        clearable=False,
        style={'width': '300px', 'margin-bottom': '20px'}
    ),
    dcc.Graph(id='donor-bar-chart')
])

# --- 2. Aid Over Time ---
aid_over_time = df.groupby('year_month')['tot_activity_value_EUR'].sum().reset_index()
fig2 = px.line(
    aid_over_time,
    x='year_month',
    y='tot_activity_value_EUR',
    markers=True,
    labels={'year_month': 'Year-Month', 'tot_activity_value_EUR': 'Total Aid (EUR)'},
    title='Aid Disbursement Over Time'
)

# --- 3. Seasonal Trends ---
monthly_trend = df.groupby('month')['tot_activity_value_EUR'].sum()
months_order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
monthly_trend = monthly_trend.reindex(months_order)
fig3 = px.bar(
    x=monthly_trend.index,
    y=monthly_trend.values,
    labels={'x': 'Month', 'y': 'Total Aid (EUR)'},
    title='Seasonal Trends: Total Aid by Month'
)

# --- 4. Timeline of Events ---
battles = {
    '2022-02-24': 'Invasion Begins',
    '2022-04-02': 'Kyiv Liberated',
    '2022-09-11': 'Kharkiv Counteroffensive',
    '2022-11-11': 'Kherson Liberated',
    '2023-06-04': 'Counteroffensive Begins',
    '2023-12-31': 'Stalemate Period'
}
monthly_aid = df.groupby(df['announcement_date'].dt.to_period('M').astype(str))['tot_activity_value_EUR'].sum()
fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=monthly_aid.index, y=monthly_aid.values, mode='lines+markers', name='Monthly Aid'))

y_levels = [0.85, 0.75]
i = 0

for date_str, label in battles.items():
    fig4.add_vline(x=date_str, line=dict(color='red', dash='dash'))
    fig4.add_annotation(
        x=date_str,
        y=max(monthly_aid) * y_levels[i % len(y_levels)],
        text=label,
        showarrow=False,
        yshift=10,
        textangle=90,
        font=dict(size=11, color='black'),
        bgcolor='white',
        bordercolor='gray',
        borderwidth=1
    )
    i += 1

fig4.update_layout(
    title='Aid Disbursement Over Time with Key Battlefield Events',
    xaxis_title='Date',
    yaxis_title='Total Aid (EUR)'
)

from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px

# Assume df and monthly_aid etc are defined as before...

# Prepare the base figure (plain line)
fig_plain = px.line(
    aid_over_time,
    x='year_month',
    y='tot_activity_value_EUR',
    markers=True,
    labels={'year_month': 'Year-Month', 'tot_activity_value_EUR': 'Total Aid (EUR)'},
    title='Aid Disbursement Over Time'
)

# Prepare the timeline figure with battle events
fig_timeline = go.Figure()
fig_timeline.add_trace(go.Scatter(x=monthly_aid.index, y=monthly_aid.values, mode='lines+markers', name='Monthly Aid'))

y_levels = [0.85, 0.75]
for i, (date_str, label) in enumerate(battles.items()):
    fig_timeline.add_vline(x=date_str, line=dict(color='red', dash='dash'))
    fig_timeline.add_annotation(
        x=date_str,
        y=max(monthly_aid) * y_levels[i % len(y_levels)],
        text=label,
        showarrow=False,
        yshift=10,
        textangle=90,
        font=dict(size=11, color='black'),
        bgcolor='white',
        bordercolor='gray',
        borderwidth=1
    )

fig_timeline.update_layout(
    title='Aid Disbursement Over Time with Key Battlefield Events',
    xaxis_title='Date',
    yaxis_title='Total Aid (EUR)'
)

# Layout part with toggle
layout = html.Div([
    html.H3("Aid Over Time Visualization"),
    dcc.RadioItems(
        id='timeline-toggle',
        options=[
            {'label': 'Plain Aid Over Time', 'value': 'plain'},
            {'label': 'Aid Over Time with Timeline', 'value': 'timeline'}
        ],
        value='plain',
        labelStyle={'display': 'inline-block', 'margin-right': '20px'}
    ),
    dcc.Graph(id='aid-time-graph', figure=fig_plain)
])

# Callback for toggling graph
@callback(
    Output('aid-time-graph', 'figure'),
    Input('timeline-toggle', 'value')
)
def toggle_timeline(selected_option):
    if selected_option == 'timeline':
        return fig_timeline
    return fig_plain


# --- 5. Aid Before vs After 2023 ---
pre = df[df['announcement_date'] < '2023-01-01']
post = df[df['announcement_date'] >= '2023-01-01']
pre_aid = pre.groupby('aid_type_general')['tot_activity_value_EUR'].sum()
post_aid = post.groupby('aid_type_general')['tot_activity_value_EUR'].sum()

fig5 = make_subplots(rows=1, cols=2, subplot_titles=('Aid Types Before 2023', 'Aid Types Since 2023'))
fig5.add_trace(go.Bar(x=pre_aid.index, y=pre_aid.values), row=1, col=1)
fig5.add_trace(go.Bar(x=post_aid.index, y=post_aid.values), row=1, col=2)
fig5.update_layout(title_text='Aid by Type: Before vs Since 2023', showlegend=False)

# --- 6. Aid Distribution Pie ---
aid_by_type = df.groupby('aid_type_general')['tot_activity_value_EUR'].sum().dropna().sort_values(ascending=False)
top = aid_by_type[:7]
if len(aid_by_type) > 7:
    top['Other'] = aid_by_type[7:].sum()
fig6 = px.pie(top, values=top.values, names=top.index, title='Aid Distribution by General Aid Type')
fig6.update_traces(
    hovertemplate='%{label}: %{value:,.0f} EUR',
    texttemplate='%{label}<br>%{value:,.0f} EUR'
)

# --- 7. Top Donor per Aid Type ---
donor_per_type = df.groupby(['aid_type_general', 'donor'])['tot_activity_value_EUR'].sum().reset_index()
idx = donor_per_type.groupby('aid_type_general')['tot_activity_value_EUR'].idxmax()
top_donors = donor_per_type.loc[idx].sort_values('tot_activity_value_EUR')
fig7 = px.bar(
    top_donors,
    x='tot_activity_value_EUR',
    y='aid_type_general',
    orientation='h',
    color='donor',
    title='Top Donor per General Aid Type',
    labels={'tot_activity_value_EUR': 'Total Aid (EUR)', 'aid_type_general': 'Aid Type'}
)

# --- Callback for Dropdown ---
@callback(
    Output('donor-bar-chart', 'figure'),
    Input('donor-sort-dropdown', 'value')
)
def update_donor_chart(sort_order):
    aid_sum = df.groupby('donor')['tot_activity_value_EUR'].sum()

    if sort_order == 'top':
        sorted_donors = aid_sum.sort_values(ascending=False).head(10)
        title = "Top 10 Donors by Total Aid (EUR)"
    else:
        sorted_donors = aid_sum.sort_values().head(10)
        title = "Bottom 10 Donors by Total Aid (EUR)"

    fig = px.bar(
        x=sorted_donors.values[::-1],
        y=sorted_donors.index[::-1],
        orientation='h',
        labels={'x': 'Total Aid (EUR)', 'y': 'Donor'},
        title=title,
        color=sorted_donors.values[::-1],
        color_continuous_scale='Blues'
    )

    fig.update_layout(margin=dict(l=150, r=50, t=50, b=50), showlegend=False)
    return fig

# --- Main Layout Export ---
financial_layout = html.Div([
    html.H2('Financial Aid to Ukraine (EUR)'),
    html.P('All aid amounts are in constant EUR, cleaned from the financialaid.csv dataset.'),
    aid_by_donor_ui,
    
    # Toggle-able Aid Over Time graph:
    html.Div([
        html.H3("Aid Over Time Visualization"),
        dcc.RadioItems(
            id='timeline-toggle',
            options=[
                {'label': 'Plain Aid Over Time', 'value': 'plain'},
                {'label': 'Aid Over Time with Timeline', 'value': 'timeline'}
            ],
            value='plain',
            labelStyle={'display': 'inline-block', 'margin-right': '20px'}
        ),
        dcc.Graph(id='aid-time-graph', figure=fig_plain)
    ]),
    
    dcc.Graph(figure=fig3),
    dcc.Graph(figure=fig5),
    dcc.Graph(figure=fig6),
    dcc.Graph(figure=fig7)
])

