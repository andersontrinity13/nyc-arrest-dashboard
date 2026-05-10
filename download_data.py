"""
download_data.py
Pulls NYPD arrest records from the NYC Open Data API (Socrata).
Grabs 50,000 rows spread across different time periods and saves
them to a local CSV for cleaning and analysis.
"""

import requests
import pandas as pd

print("Downloading NYC Arrest data...")

# NYC Open Data endpoint for NYPD arrest records
url = "https://data.cityofnewyork.us/resource/8h9b-rp9u.json"

all_data = []

# Pull 4 batches of 12,500 rows from different offsets so we get
# arrests spread across the full dataset rather than just the most recent
offsets = [50000, 150000, 250000, 350000]

for offset in offsets:
    params = {
        "$limit": 12500,   # rows per request (API max is 50k but we keep it light)
        "$offset": offset  # skip ahead in the dataset to get different time periods
    }

    response = requests.get(url, params=params)
    batch = response.json()
    all_data.extend(batch)
    print(f"Got {len(batch)} rows from offset {offset}")

# Combine all batches into a single dataframe
df = pd.DataFrame(all_data)

# Save raw data to CSV before any cleaning happens
df.to_csv("arrests.csv", index=False)

print(f"Done! Downloaded {len(df)} rows total.")
print(df['arrest_date'].min(), "to", df['arrest_date'].max())
