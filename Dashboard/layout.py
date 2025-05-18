# === layout.py ===
from dash import dcc, html
from sections.economic import economic_layout
from sections.financialaid import financial_layout
from sections.russian_losses import russian_losses_layout
from sections.equipment_losses import equipment_layout

def create_layout(app):
    return html.Div([
        dcc.Tabs([
            dcc.Tab(label='Economic Indicators', children=economic_layout),
            dcc.Tab(label='Financial Aid to Ukraine', children=financial_layout),
            dcc.Tab(label='Russian Losses', children=russian_losses_layout),
            dcc.Tab(label='Equipment Losses', children=equipment_layout),
            # Future tabs go here
        ])
    ])
