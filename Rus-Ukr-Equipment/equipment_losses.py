# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
from math import sqrt
import warnings
warnings.filterwarnings('ignore')

# %%
# Load the data
df = pd.read_excel('Russia-Ukraine Equipment Losses.xlsx', sheet_name='Original')

# %%
df.info()

# %%
# Data Preprocessing
# ------------------

# Convert date to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Set date as index
df.set_index('Date', inplace=True)

# Fill any missing values with forward fill
df.fillna(method='ffill', inplace=True)

# Create a subset with key metrics
key_metrics = df[['Russia_Total', 'Ukraine_Total', 'Ratio RU/UA', 
                  'Russia_Destroyed', 'Ukraine_Destroyed',
                  'Russia_Tanks', 'Ukraine_Tanks',
                  'Russia_Aircraft', 'Ukraine_Aircraft',
                  'Russia_Artillery', 'Ukraine_Artillery']]

# %%
df[['Russia_Total', 'Ukraine_Total', 'Ratio RU/UA', 
                  'Russia_Destroyed', 'Ukraine_Destroyed',
                  'Russia_Tanks', 'Ukraine_Tanks',
                  'Russia_Aircraft', 'Ukraine_Aircraft',
                  'Russia_Artillery', 'Ukraine_Artillery',]].isnull().any()

# %%
# Exploratory Data Analysis (EDA)
# ------------------------------

# Plotting overall equipment losses
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Russia_Total'], label='Russia Total Losses', color='red')
plt.plot(df.index, df['Ukraine_Total'], label='Ukraine Total Losses', color='blue')
plt.title('Total Equipment Losses Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Equipment Lost')
plt.legend()
plt.grid(True)
plt.show()

# %%
# Plotting ratio of losses
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Ratio RU/UA'], label='Russia/Ukraine Loss Ratio', color='purple')
plt.axhline(y=1, color='black', linestyle='--', label='1:1 Ratio')
plt.title('Ratio of Russian to Ukrainian Equipment Losses Over Time')
plt.xlabel('Date')
plt.ylabel('Loss Ratio')
plt.legend()
plt.grid(True)
plt.show()


# %%
# Plotting destroyed equipment
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Russia_Destroyed'], label='Russia Destroyed', color='red')
plt.plot(df.index, df['Ukraine_Destroyed'], label='Ukraine Destroyed', color='blue')
plt.title('Destroyed Equipment Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Equipment Destroyed')
plt.legend()
plt.grid(True)
plt.show()

# %%
# Plotting specific equipment types
equipment_types = ['Tanks', 'Aircraft', 'Artillery']

for equipment in equipment_types:
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df[f'Russia_{equipment}'], label=f'Russia {equipment}', color='red')
    plt.plot(df.index, df[f'Ukraine_{equipment}'], label=f'Ukraine {equipment}', color='blue')
    plt.title(f'{equipment} Losses Over Time')
    plt.xlabel('Date')
    plt.ylabel(f'Number of {equipment} Lost')
    plt.legend()
    plt.grid(True)
plt.show()

# %%
# Check for negative differences (which cause drops in cumulative count)
df['rus_aircraft_daily_change'] = df['Russia_Aircraft'].diff()
negative_changes = df[df['rus_aircraft_daily_change'] < 0]
print(negative_changes[['Russia_Aircraft', 'rus_aircraft_daily_change']])

# %%
# Check for negative differences (which cause drops in cumulative count)
df['ukr_aircraft_daily_change'] = df['Ukraine_Aircraft'].diff()
negative_changes = df[df['ukr_aircraft_daily_change'] < 0]
print(negative_changes[['Ukraine_Aircraft', 'ukr_aircraft_daily_change']])

# %%
# Find the drop amount on 2023-03-27
drop_date = '2023-03-27'
drop_value = df.loc[df.index == drop_date, 'Ukraine_Aircraft'].values[0]
prev_value = df.loc[df.index < drop_date, 'Ukraine_Aircraft'].max()  # Last value before drop

drop_amount = prev_value - drop_value  # How much was subtracted?

# Apply correction: Reduce all values AFTER the drop by the same amount
df['Ukraine_Aircraft'] = df['Ukraine_Aircraft'].copy()
df.loc[df.index >= drop_date, 'Ukraine_Aircraft'] += drop_amount

# %%
# Find the drop amount on 2022-11-15
drop_date = '2022-11-15'
drop_value = df.loc[df.index == drop_date, 'Russia_Aircraft'].values[0]
prev_value = df.loc[df.index < drop_date, 'Russia_Aircraft'].max()  # Last value before drop

drop_amount = prev_value - drop_value  # How much was subtracted?

# Apply correction: Reduce all values AFTER the drop by the same amount
df['Russia_Aircraft'] = df['Russia_Aircraft'].copy()
df.loc[df.index >= drop_date, 'Russia_Aircraft'] += drop_amount

# %%
# Plotting specific equipment types
equipment_types = ['Aircraft_fixed']

for equipment in equipment_types:
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df[f'Russia_{equipment}'], label=f'Russia {equipment}', color='red')
    plt.plot(df.index, df[f'Ukraine_{equipment}'], label=f'Ukraine {equipment}', color='blue')
    plt.title(f'{equipment} Losses Over Time')
    plt.xlabel('Date')
    plt.ylabel(f'Number of {equipment} Lost')
    plt.legend()
    plt.grid(True)
plt.show()

# %%
# Data Analysis
# -------------

# Calculate correlation matrix
corr_matrix = key_metrics.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix of Key Metrics')
plt.show()

# %%
"""
## Perfect correlation is suspicious
### Further investigate
"""

# %%
plt.plot(df.index, df['Russia_Tanks'], label='Russia Tanks')
plt.plot(df.index, df['Ukraine_Tanks'], label='Ukraine Tanks')
plt.legend()
plt.title("Tank Losses Over Time")
plt.xlabel("Date")
plt.ylabel("Tank Losses")
plt.grid(True)
plt.show()


# %%
plt.scatter(df['Russia_Tanks'], df['Ukraine_Tanks'])
plt.xlabel('Russia Tanks')
plt.ylabel('Ukraine Tanks')
plt.title('Scatter Plot of Tank Losses')
plt.grid(True)
plt.show()


# %%
df[['Russia_Tanks', 'Ukraine_Tanks']].corr()

# %%
"""
### The losses are likely strongly associated, which could point to:

    Symmetrical combat operations

    Similar reporting windows

    A shared escalation timeline (e.g., both sides increased tank deployments together)
"""

# %%
# Finding whether daily changes move together
df['Russia_Tank_Change'] = df['Russia_Tanks'].diff()
df['Ukraine_Tank_Change'] = df['Ukraine_Tanks'].diff()
df[['Russia_Tank_Change', 'Ukraine_Tank_Change']].corr()

# %%
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.plot(df.index, df['Russia_Tank_Change'], label='Russia Daily Tank Losses', alpha=0.7)
plt.plot(df.index, df['Ukraine_Tank_Change'], label='Ukraine Daily Tank Losses', alpha=0.7)
plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
plt.title('Daily Tank Losses Over Time')
plt.xlabel('Date')
plt.ylabel('Daily Tank Losses')
plt.legend()
plt.grid(True)
plt.show()

# %%
"""
### Clip the changes which are negative since they could be errors
"""

# %%
# Clip negative values to zero (keep only valid positive losses)
df['Russia_Tank_Change'] = df['Russia_Tank_Change'].clip(lower=0)
df['Ukraine_Tank_Change'] = df['Ukraine_Tank_Change'].clip(lower=0)

# %%
plt.figure(figsize=(12, 5))
plt.plot(df.index, df['Russia_Tank_Change'], label='Russia Daily Tank Losses', alpha=0.7)
plt.plot(df.index, df['Ukraine_Tank_Change'], label='Ukraine Daily Tank Losses', alpha=0.7)
plt.title('Daily Tank Losses After Clipping Negatives')
plt.xlabel('Date')
plt.ylabel('Tank Losses')
plt.legend()
plt.grid(True)
plt.show()


# %%
corr = df[['Russia_Tank_Change', 'Ukraine_Tank_Change']].corr().iloc[0, 1]
print(f"Correlation of Daily Tank Losses (post-clipping): {corr:.3f}")

# %%
rus_thresh = df['Russia_Tank_Change'].quantile(0.90)
ukr_thresh = df['Ukraine_Tank_Change'].quantile(0.90)

# Create spike flags
df['Russia_Spike'] = df['Russia_Tank_Change'] > rus_thresh
df['Ukraine_Spike'] = df['Ukraine_Tank_Change'] > ukr_thresh

# Check days when both spike
simultaneous_spikes = df[df['Russia_Spike'] & df['Ukraine_Spike']]

print(f"📅 Number of days both sides had spike tank losses: {len(simultaneous_spikes)}")
display(simultaneous_spikes[['Russia_Tank_Change', 'Ukraine_Tank_Change']])


# %%
"""
### This will show how often both sides experienced unusually high losses on the same day, which could suggest:

    Major battles

    Artillery duels

    Strategic offensives

    For instance:
        2022-02-28 - Early days of the full-scale invasion (Battle of Kyiv, Kharkiv, and other cities began in late February 2022)
"""

# %%
# Data Prediction (Forecasting)
# ----------------------------

# Extract total cumulative losses time series for both Russia and Ukraine
russia_ts = df['Russia_Total']
ukraine_ts = df['Ukraine_Total']

# Reserve the last 30 days of data for testing, use the rest for training
train_size = len(russia_ts) - 30
train_rus, test_rus = russia_ts[0:train_size], russia_ts[train_size:]
train_ukr, test_ukr = ukraine_ts[0:train_size], ukraine_ts[train_size:]

# Fit ARIMA model (order=2,1,2) on Russia's training data
model_rus = ARIMA(train_rus, order=(2,1,2))
model_rus_fit = model_rus.fit()

# Forecast Russia's cumulative losses for the next 30 days (same as test set)
forecast_rus = model_rus_fit.forecast(steps=30)

# Fit ARIMA model (order=2,1,2) on Ukraine's training data
model_ukr = ARIMA(train_ukr, order=(2,1,2))
model_ukr_fit = model_ukr.fit()

# Forecast Ukraine's cumulative losses for the next 30 days
forecast_ukr = model_ukr_fit.forecast(steps=30)

# Evaluate forecast accuracy using RMSE (Root Mean Squared Error)
rmse_rus = sqrt(mean_squared_error(test_rus, forecast_rus))
rmse_ukr = sqrt(mean_squared_error(test_ukr, forecast_ukr))

# Print RMSE values to assess model performance
print(f"Russia Forecast RMSE: {rmse_rus:.2f}")
print(f"Ukraine Forecast RMSE: {rmse_ukr:.2f}")


# %%
# Forecast 180 days ahead for Russia
future_forecast_rus = model_rus_fit.forecast(steps=180)

# Forecast 180 days ahead for Ukraine
future_forecast_ukr = model_ukr_fit.forecast(steps=180)


# %%
# Use last timestamp from DatetimeIndex
last_date = df.index[-1]

# Generate 365 future dates
future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=180)

# Create forecast DataFrame
forecast_df = pd.DataFrame({
    'Date': future_dates,
    'Russia_Forecast': future_forecast_rus,
    'Ukraine_Forecast': future_forecast_ukr
})


# %%
plt.figure(figsize=(12, 6))

# Plot historical data
plt.plot(df.index, df['Russia_Total'], label='Russia Actual', color='blue')
plt.plot(df.index, df['Ukraine_Total'], label='Ukraine Actual', color='green')

# Plot forecasted data
plt.plot(forecast_df['Date'], forecast_df['Russia_Forecast'], label='Russia Forecast', color='red', linestyle='--')
plt.plot(forecast_df['Date'], forecast_df['Ukraine_Forecast'], label='Ukraine Forecast', color='orange', linestyle='--')

plt.title('half-Year Forecast of Total Losses')
plt.xlabel('Date')
plt.ylabel('Total Losses')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# %%
# Get the last known actual value
latest_rus_total = df['Russia_Total'].iloc[-1]
latest_ukr_total = df['Ukraine_Total'].iloc[-1]

# Get the final forecasted total after 1 year
forecasted_rus_total = future_forecast_rus.iloc[-1]
forecasted_ukr_total = future_forecast_ukr.iloc[-1]

# Compute expected additional losses
russia_additional = forecasted_rus_total - latest_rus_total
ukraine_additional = forecasted_ukr_total - latest_ukr_total

print(f"Forecasted Additional Russia Losses (next half year): {russia_additional:.0f}")
print(f"Forecasted Additional Ukraine Losses (next half year): {ukraine_additional:.0f}")


# %%
# Advanced Visualization
# ----------------------

# Cumulative losses by equipment type
equipment_cols = ['Russia_Tanks', 'Russia_Aircraft', 'Russia_Artillery',
                 'Ukraine_Tanks', 'Ukraine_Aircraft', 'Ukraine_Artillery']

plt.figure(figsize=(14, 7))
for col in equipment_cols:
    plt.plot(df.index, df[col], label=col)
plt.title('Cumulative Equipment Losses by Type')
plt.xlabel('Date')
plt.ylabel('Number of Equipment Lost')
plt.legend()
plt.grid(True)
plt.show()

# Loss ratio distribution
plt.figure(figsize=(10, 6))
sns.histplot(df['Ratio RU/UA'], bins=30, kde=True, color='purple')
plt.title('Distribution of Russia/Ukraine Loss Ratio')
plt.xlabel('Loss Ratio')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

# Monthly aggregated losses
monthly_data = df.resample('M').last()
plt.figure(figsize=(14, 7))
plt.plot(monthly_data.index, monthly_data['Russia_Total'], label='Russia Monthly', marker='o', color='red')
plt.plot(monthly_data.index, monthly_data['Ukraine_Total'], label='Ukraine Monthly', marker='o', color='blue')
plt.title('Monthly Aggregated Equipment Losses')
plt.xlabel('Month')
plt.ylabel('Total Equipment Lost')
plt.legend()
plt.grid(True)
plt.show()

# %%
