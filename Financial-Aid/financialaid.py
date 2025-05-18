import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load Dataset ---
df = pd.read_csv('financialaid.csv')

# --- Data Cleaning ---
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

df['aid_type_general'] = df['aid_type_general'].astype(str).str.strip().str.title()
df['aid_type_general'] = df['aid_type_general'].replace(['Nan', ''], pd.NA)

categorical_cols = ['donor', 'aid_type_general', 'aid_type_specific']
for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].astype('category')

df['year_month'] = df['announcement_date'].dt.to_period('M')
df['month'] = df['announcement_date'].dt.month_name()
df['year'] = df['announcement_date'].dt.year

# --- Visualization 1: Total Aid by Donor ---
aid_by_donor = df.groupby('donor')['tot_activity_value_EUR'].sum().sort_values(ascending=False)
plt.figure(figsize=(12, 7))
aid_by_donor.head(10).plot(kind='barh', color='skyblue')
plt.xlabel('Total Aid (EUR)')
plt.ylabel('Donor')
plt.title('Top 10 Donors by Total Aid (EUR)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# --- Visualization 2: Aid Over Time (Monthly) ---
aid_over_time = df.groupby('year_month')['tot_activity_value_EUR'].sum()
plt.figure(figsize=(12, 6))
aid_over_time.plot(kind='line', marker='o')
plt.xlabel('Year-Month')
plt.ylabel('Total Aid (EUR)')
plt.title('Aid Disbursement Over Time')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --- Visualization 3: Seasonal Trends ---
df['month'] = df['announcement_date'].dt.month_name()
monthly_trend = df.groupby('month')['tot_activity_value_EUR'].sum()
months_order = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]
monthly_trend = monthly_trend.reindex(months_order)
plt.figure(figsize=(12, 6))
sns.barplot(x=monthly_trend.index, y=monthly_trend.values, palette='coolwarm')
plt.title('Seasonal Trends: Total Aid by Month')
plt.xticks(rotation=45)
plt.ylabel('Total Aid (EUR)')
plt.tight_layout()
plt.show()

# --- Visualization 4: Battlefield Events Timeline (Improved) ---
battles = {
    '2022-02-24': 'Invasion Begins',
    '2022-04-02': 'Kyiv Liberated',
    '2022-09-11': 'Kharkiv Counteroffensive',
    '2022-11-11': 'Kherson Liberated',
    '2023-06-04': 'Ukrainian Counteroffensive Begins',
    '2023-12-31': 'Stalemate Period'
}

df['announcement_date'] = pd.to_datetime(df['announcement_date'], errors='coerce')
aid_over_time = df.groupby('announcement_date')['tot_activity_value_EUR'].sum().resample('M').sum()

plt.figure(figsize=(14, 6))
plt.plot(aid_over_time.index, aid_over_time.values, marker='o', label='Monthly Aid (EUR)', color='navy')

# Improved annotations: staggered placement
offsets = [0.95, 0.80, 0.90, 0.75, 0.88, 0.70]
for i, (date_str, label) in enumerate(battles.items()):
    date = pd.to_datetime(date_str)
    y = max(aid_over_time) * offsets[i]
    plt.axvline(date, color='red', linestyle='--', linewidth=1)
    plt.text(date, y, label, rotation=90, ha='right', va='top',
             fontsize=9, color='darkred', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

plt.title("Aid Disbursement Over Time with Key Battlefield Events")
plt.xlabel("Date")
plt.ylabel("Total Monthly Aid (EUR)")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Visualization 5: Before vs After 2023 ---
df_pre = df[df['announcement_date'] < '2023-01-01']
df_post = df[df['announcement_date'] >= '2023-01-01']

pre_aid = df_pre.groupby('aid_type_general')['tot_activity_value_EUR'].sum().sort_values(ascending=False)
post_aid = df_post.groupby('aid_type_general')['tot_activity_value_EUR'].sum().sort_values(ascending=False)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
pre_aid.plot(kind='bar', ax=axes[0], color='orange', title='Aid Types Before 2023')
post_aid.plot(kind='bar', ax=axes[1], color='green', title='Aid Types Since 2023')

for ax in axes:
    ax.set_ylabel('Total Aid (EUR)')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

plt.tight_layout()
plt.show()

# --- Visualization 6: Aid Distribution Pie Chart ---
aid_by_type = df.groupby('aid_type_general')['tot_activity_value_EUR'].sum().sort_values(ascending=False).dropna()
top_n = 7
if len(aid_by_type) > top_n:
    top = aid_by_type[:top_n]
    other = aid_by_type[top_n:].sum()
    aid_by_type = top.append(pd.Series({'Other': other}))

plt.figure(figsize=(8, 6))
aid_by_type.plot(kind='pie', autopct='%1.1f%%', startangle=140)
plt.ylabel('')
plt.title('Aid Distribution by General Aid Type')
plt.tight_layout()
plt.show()

# --- Visualization 7: Top Donor per General Aid Type ---
top_donor_per_type = (
    df.groupby(['aid_type_general', 'donor'])['tot_activity_value_EUR']
    .sum()
    .reset_index()
)
idx = top_donor_per_type.groupby('aid_type_general')['tot_activity_value_EUR'].idxmax()
top_donor_per_type = top_donor_per_type.loc[idx].sort_values('tot_activity_value_EUR', ascending=True)

plt.figure(figsize=(12, 8))
plt.barh(top_donor_per_type['aid_type_general'], top_donor_per_type['tot_activity_value_EUR'], color='seagreen')

for index, value in enumerate(top_donor_per_type['tot_activity_value_EUR']):
    donor = top_donor_per_type['donor'].iloc[index]
    plt.text(value, index, f"{donor} ({int(value):,} EUR)", va='center', fontsize=9)

plt.xlabel('Total Aid (EUR)')
plt.title('Top Donor per General Aid Type')
plt.tight_layout()
plt.show()
