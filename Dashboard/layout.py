# === layout.py ===
from dash import dcc, html
from sections.economic import economic_layout
from sections.financialaid import financial_layout
from sections.russian_losses import russian_losses_layout
from sections.equipment_losses import equipment_layout
from sections.forecast_layout import forecast_layout
from sections.civilians import civilians_layout
from sections.ukr_civilian_losses import ukraine_map_layout


def create_layout(app):
    return html.Div([
        dcc.Tabs([
            dcc.Tab(label='Economic Indicators', children=economic_layout),
            dcc.Tab(label='Financial Aid to Ukraine', children=financial_layout),
            dcc.Tab(label='Russian Losses', children=russian_losses_layout),
            dcc.Tab(label='Equipment Losses', children=equipment_layout),
            dcc.Tab(label='Loss Forecasting', children=[forecast_layout]),
            dcc.Tab(label='Civilian losses', children=[civilians_layout]),
            dcc.Tab(label='Ukraine Civilian losses', children=[ukraine_map_layout])
            # Future tabs go here
        ])
    ])
