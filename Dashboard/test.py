import plotly.graph_objects as go
from dash import Dash, html, dcc

# Create a simple map with test marker
fig = go.Figure(go.Scattermapbox(
    lon=[31.260471],  # Cherkasy Oblast longitude
    lat=[49.287462],  # Cherkasy Oblast latitude
    mode='markers+text',
    marker=go.scattermapbox.Marker(
        size=20,
        color='red'
    ),
    text=["Test Marker (Cherkasy)"],
    textposition="top right"
))

# Configure map layout
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=5,
    mapbox_center={"lat": 48.5, "lon": 31.5},
    margin={"r":0,"t":0,"l":0,"b":0},
    height=600
)

# Create Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Ukraine Map Marker Test"),
    dcc.Graph(figure=fig),
    html.Div([
        html.P("Testing marker at coordinates: 31.260471, 49.287462"),
        html.P("This should appear near Cherkasy Oblast")
    ], style={'text-align': 'center'})
])

if __name__ == '__main__':
    app.run(debug=True)