import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, Dash

# Load csv
df = pd.read_csv('../Rus-Ukr-Civilians/ukraine-civilian-preprocessed.csv')

# Load and verify GeoJSON
with open('../Rus-Ukr-Civilians/ukraine_oblasts.geojson') as f:
    geojson = json.load(f)

# Enhanced centroid calculator with validation
def get_centroid(feature):
    geom = feature['geometry']
    if geom['type'] not in ['Polygon', 'MultiPolygon']:
        raise ValueError(f"Unsupported geometry type: {geom['type']}")
            
    coords = geom['coordinates']
    if geom['type'] == 'MultiPolygon':
        coords = coords[0]  # Use first polygon for centroid
            
    lons, lats = zip(*coords[0])  # Extract first ring coordinates
    return {
        "name": feature['properties']['name:en'],
        "lon": sum(lons)/len(lons),
        "lat": sum(lats)/len(lats),
    }

# Calculate centroids with error tracking
centroids = [get_centroid(f) for f in geojson['features']]
centroid_df = pd.DataFrame(centroids)

# Name normalization with case-insensitive matching
df['Area_normalized'] = df['Area'].str.strip().str.lower()
centroid_df['name_normalized'] = centroid_df['name'].str.strip().str.lower()


# Create mapping with fallbacks
name_mapping = {
    'kyiv oblast': 'kiev oblast',
    'kyiv (city)': 'kiev oblast',  # Map to same coords as oblast
    'odesa oblast': 'odessa oblast',
    'zaporizhzhia oblast': 'zaporizhia oblast'
}

# Apply mapping with verification
df['Area_mapped'] = df['Area_normalized'].map(name_mapping).fillna(df['Area_normalized'])
unmapped = df[~df['Area_mapped'].isin(centroid_df['name_normalized'])]

# Merge with validation
df_merged = pd.merge(
    df,
    centroid_df,
    left_on='Area_mapped',
    right_on='name_normalized',
    how='left'
)

valid_labels = df_merged.dropna(subset=['lon', 'lat'])


# Main visualization
main_fig = px.choropleth_mapbox(
    df_merged,
    geojson=geojson,
    locations='Area',
    featureidkey='properties.name:en',
    color='Fatalities',
    color_continuous_scale='Reds',
    mapbox_style='carto-positron',
    zoom=5,
    center={'lat': 48.5, 'lon': 31.5},
    opacity=0.7
)

# Add labels only for valid points
if not valid_labels.empty:
    main_fig.add_trace(go.Scattermapbox(
        lon=valid_labels['lon'],
        lat=valid_labels['lat'],
        mode='text',
        text=valid_labels['Fatalities'].astype(str),
        textfont=dict(size=12, color='black'),
        hoverinfo='skip'
    ))

# Create Dash app with debug view
app = Dash(__name__)
app.layout = html.Div([

    html.H2("Final Visualization"),
    html.Div([
        dcc.Graph(figure=main_fig, style={'height': '60vh'})
    ]),
])

if __name__ == '__main__':
    print("\n🚀 Starting debug server...")
    app.run(debug=True)