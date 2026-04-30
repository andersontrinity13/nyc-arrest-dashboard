import pandas as pd

df = pd.read_csv("arrests.csv")
print(f"Starting shape: {df.shape}")

# Keep only the columns we actually need
cols_to_keep = [
    'arrest_key', 'arrest_date', 'ofns_desc', 'pd_desc',
    'law_cat_cd', 'arrest_boro', 'arrest_precinct',
    'age_group', 'perp_sex', 'perp_race',
    'latitude', 'longitude'
]
df = df[cols_to_keep]

# Convert arrest_date to a real date
df['arrest_date'] = pd.to_datetime(df['arrest_date'])

# Pull out month and year
df['arrest_month'] = df['arrest_date'].dt.month
df['arrest_year'] = df['arrest_date'].dt.year
df['arrest_month_name'] = df['arrest_date'].dt.strftime('%B')

# Add season column
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

df['season'] = df['arrest_month'].apply(get_season)

# Add hot/cold label (simple version based on NYC averages)
def get_temp_category(month):
    if month in [6, 7, 8, 9]:
        return 'Hot (Jun-Sep)'
    elif month in [12, 1, 2, 3]:
        return 'Cold (Dec-Mar)'
    else:
        return 'Mild (Apr-May, Oct-Nov)'

df['temp_category'] = df['arrest_month'].apply(get_temp_category)

# Map borough codes to real names
boro_map = {
    'B': 'Bronx',
    'S': 'Staten Island',
    'K': 'Brooklyn',
    'M': 'Manhattan',
    'Q': 'Queens'
}
df['borough_name'] = df['arrest_boro'].map(boro_map)

# Map law category codes to readable labels
law_map = {
    'F': 'Felony',
    'M': 'Misdemeanor',
    'V': 'Violation',
    'I': 'Infraction'
}
df['law_category'] = df['law_cat_cd'].map(law_map)

# Drop rows missing critical fields
df = df.dropna(subset=['ofns_desc', 'borough_name', 'law_category'])

# Standardize text
df['ofns_desc'] = df['ofns_desc'].str.title()
df['pd_desc'] = df['pd_desc'].str.title()

print(f"Cleaned shape: {df.shape}")
print("\nSeason breakdown:")
print(df['season'].value_counts())
print("\nTemp category breakdown:")
print(df['temp_category'].value_counts())

df.to_csv("arrests_clean.csv", index=False)
print("\nSaved as arrests_clean.csv")