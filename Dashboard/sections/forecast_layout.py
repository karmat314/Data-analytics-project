import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from dash import html
from matplotlib.ticker import FuncFormatter

# Load the original data and forecast data
df = pd.read_csv('../Rus-Ukr-Equipment/ukr-rus-equipment_cleaned.csv')
forecast_df = pd.read_csv('../Rus-Ukr-Equipment/forecast.csv')

# Convert dates to datetime
df['Date'] = pd.to_datetime(df['Date'])
forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])

# Set index for original data
df.set_index('Date', inplace=True)

# Formatting function for y-axis
def thousands_formatter(x, pos):
    return f'{int(x/1000)}K'

fig, ax1 = plt.subplots(figsize=(14, 8))  # Single plot with adjusted height

# Main plot - Cumulative losses
ax1.plot(df.index, df['Russia_Total'], label='Russia Actual', color='#E53935', linewidth=2)
ax1.plot(df.index, df['Ukraine_Total'], label='Ukraine Actual', color='#1E88E5', linewidth=2)
ax1.plot(forecast_df['Date'], forecast_df['Russia_Forecast'], label='Russia Forecast', color='#B71C1C', linestyle='--')
ax1.plot(forecast_df['Date'], forecast_df['Ukraine_Forecast'], label='Ukraine Forecast', color='#0D47A1', linestyle='--')

# Formatting
ax1.set_title('6-Month Forecast of Total Equipment Losses in Russia-Ukraine War', 
             fontsize=16, pad=20, fontweight='bold')
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Total Equipment Losses', fontsize=12)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

# Add vertical line for forecast start
last_date = df.index[-1]
ax1.axvline(x=last_date, color='gray', linestyle=':', linewidth=1.5)
ax1.text(last_date - pd.Timedelta(days=60), ax1.get_ylim()[1]*0.9, 
        'Forecast Start', rotation=0, color='gray')

# Add annotation with forecast values
last_rus = int(forecast_df['Russia_Forecast'].iloc[-1])
last_ukr = int(forecast_df['Ukraine_Forecast'].iloc[-1])
ax1.annotate(f'Russia: ~{last_rus:,}', 
            xy=(forecast_df['Date'].iloc[-1], forecast_df['Russia_Forecast'].iloc[-1]),
            xytext=(10, 10), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='#FFEBEE', ec='#B71C1C'),
            color='#B71C1C')
ax1.annotate(f'Ukraine: ~{last_ukr:,}', 
            xy=(forecast_df['Date'].iloc[-1], forecast_df['Ukraine_Forecast'].iloc[-1]),
            xytext=(10, -25), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='#E3F2FD', ec='#0D47A1'),
            color='#0D47A1')

plt.tight_layout()

# Convert to base64 image
buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
buf.seek(0)
encoded_img = base64.b64encode(buf.read()).decode()

# Create layout with additional information
forecast_layout = html.Div([
    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(encoded_img), 
                style={'width': '100%', 'maxWidth': '1000px', 'display': 'block', 'margin': '0 auto'})
    ]),
    
    html.Div([
        html.H4("Forecast Insights:", style={'color': '#2c3e50', 'marginTop': '20px'}),
        html.Ul([
            html.Li(f"Current Russian losses: {int(df['Russia_Total'].iloc[-1]):,}"),
            html.Li(f"Current Ukrainian losses: {int(df['Ukraine_Total'].iloc[-1]):,}"),
            html.Li(f"Projected Russian losses in 6 months: ~{last_rus:,}"),
            html.Li(f"Projected Ukrainian losses in 6 months: ~{last_ukr:,}"),
            html.Li("Forecast based on ARIMA modeling of historical patterns"),
        ], style={'lineHeight': '1.8'}),
        
        html.P("Note: This forecast is based on historical patterns and doesn't account for potential changes in war intensity, strategy, or external factors.",
              style={'fontStyle': 'italic', 'color': '#7f8c8d', 'marginTop': '15px'})
    ], style={'maxWidth': '900px', 'margin': '20px auto', 'padding': '15px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'})