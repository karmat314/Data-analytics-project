from dash import Input, Output
from sections.economic import df_all_melted
import plotly.express as px

# Import equipment section callback registrar
from sections.equipment_losses import register_callbacks as register_equipment_callbacks

def register_callbacks(app):
    # Existing economic callback
    @app.callback(
        Output('indicator-lineplot', 'figure'),
        Input('indicator-dropdown', 'value')
    )
    def update_economic_plot(indicator):
        filtered = df_all_melted[df_all_melted['Indicator'] == indicator]
        fig = px.line(
            filtered, x='Year', y='Value', color='Country',
            markers=True, title=indicator
        )
        fig.update_layout(title_x=0.5)
        return fig

    # Register equipment callbacks here as well
    register_equipment_callbacks(app)
