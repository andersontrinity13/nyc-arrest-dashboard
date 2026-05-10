"""
clean_data.py
Takes the raw arrests.csv pulled from the NYC Open Data API and transforms
it into a clean, analysis-ready dataset. Handles column selection, date
parsing, feature engineering (season, temp category), and label mapping.
Output is saved as arrests_clean.csv for use in the Streamlit dashboard.
"""

import pandas as pd

df = pd.read_csv("arrests.csv")
print(f"Starting shape: {df.shape}")

# Drop columns we don't need for analysis — keeps the dataset lean
cols_to_keep = [
    'arrest_key', 'arrest_date', 'ofns_desc', 'pd_desc',
    'law_cat_cd', 'arrest_boro', 'arrest_precinct',
    'age_group', 'perp_sex', 'perp_race',
    'latitude', 'longitude'
]
df = df[cols_to_keep]

# Parse arrest_date as a proper datetime so we can extract month/year/season
df['arrest_date'] = pd.to_datetime(df['arrest_date'])

# Pull out time components we'll use for grouping and trend analysis
df['arrest_month'] = df['arrest_date'].dt.month
df['arrest_year'] = df['arrest_date'].dt.year
df['arrest_month_name'] = df['arrest_date'].dt.strftime('%B')


def get_season(month):
    """Assign a season label based on the month number."""
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

df['season'] = df['arrest_month'].apply(get_season)


def get_temp_category(month):
    """
    Bucket months into broad temperature categories for weather correlation.
    Used in the dashboard to compare arrest patterns across hot, cold, and mild periods.
    """
    if month in [6, 7, 8, 9]:
        return 'Hot (Jun-Sep)'
    elif month in [12, 1, 2, 3]:
        return 'Cold (Dec-Mar)'
    else:
        return 'Mild (Apr-May, Oct-Nov)'

df['temp_category'] = df['arrest_month'].apply(get_temp_category)

# The raw data uses single-letter borough codes — map them to full names
# so charts and filters are readable
boro_map = {
    'B': 'Bronx',
    'S': 'Staten Island',
    'K': 'Brooklyn',
    'M': 'Manhattan',
    'Q': 'Queens'
}
df['borough_name'] = df['arrest_boro'].map(boro_map)

# Same for law category — convert codes to human-readable labels
law_map = {
    'F': 'Felony',
    'M': 'Misdemeanor',
    'V': 'Violation',
    'I': 'Infraction'
}
df['law_category'] = df['law_cat_cd'].map(law_map)

# Remove rows where key fields are missing — can't analyze what we can't label
df = df.dropna(subset=['ofns_desc', 'borough_name', 'law_category'])

# Standardize text casing so offense descriptions display consistently in charts
df['ofns_desc'] = df['ofns_desc'].str.title()
df['pd_desc'] = df['pd_desc'].str.title()

print(f"Cleaned shape: {df.shape}")
print("\nSeason breakdown:")
print(df['season'].value_counts())
print("\nTemp category breakdown:")
print(df['temp_category'].value_counts())

# Save the cleaned dataset — this is what app.py loads
df.to_csv("arrests_clean.csv", index=False)
print("\nSaved as arrests_clean.csv")
