# === sections/economic.py ===
from dash import dcc, html
import pandas as pd

# Load data
df_russia = pd.read_csv('../Rus-Ukr-Economy/russia_eco_indicators.csv', skiprows=4)
df_ukraine = pd.read_csv('../Rus-Ukr-Economy/ukr_eco_indicators.csv', skiprows=4)

indicators_to_keep = [
    'GDP (current US$)',
    'GDP growth (annual %)',
    'GDP per capita (current US$)',
    'Unemployment, total (% of total labor force) (national estimate)',
    'Inflation, consumer prices (annual %)',
    'Exports of goods and services (% of GDP)',
    'Imports of goods and services (% of GDP)',
    'External balance on goods and services (current US$)'
]

def prepare_df(df):
    df = df[df['Indicator Name'].isin(indicators_to_keep)]
    year_cols = [str(year) for year in range(2014, 2024)]
    df = df[['Indicator Name'] + year_cols]
    df = df.set_index('Indicator Name').T.reset_index().rename(columns={'index': 'Year'})
    df['Year'] = df['Year'].astype(int)
    for col in indicators_to_keep:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

df_russia = prepare_df(df_russia)
df_ukraine = prepare_df(df_ukraine)

df_russia['Country'] = 'Russia'
df_ukraine['Country'] = 'Ukraine'
df_all = pd.concat([df_russia, df_ukraine])
df_all_melted = df_all.melt(id_vars=['Year', 'Country'], var_name='Indicator', value_name='Value')

economic_layout = html.Div([
    html.H2("Economic Indicators", style={'textAlign': 'center'}),
    html.Label("Select Economic Indicator:"),
    dcc.Dropdown(
        id='indicator-dropdown',
        options=[{'label': ind, 'value': ind} for ind in indicators_to_keep],
        value='GDP (current US$)',
        clearable=False,
        style={'width': '60%'}
    ),
    dcc.Graph(id='indicator-lineplot', style={'height': '600px'})
])
