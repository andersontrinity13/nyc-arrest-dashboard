import requests
import pandas as pd

print("Downloading NYC Arrest data...")

url = "https://data.cityofnewyork.us/resource/8h9b-rp9u.json"

all_data = []

# Pull 4 batches of 12500 rows each from different offsets to get spread across the year
offsets = [50000, 150000, 250000, 350000]

for offset in offsets:
    params = {
        "$limit": 12500,
        "$offset": offset
    }
    response = requests.get(url, params=params)
    batch = response.json()
    all_data.extend(batch)
    print(f"Got {len(batch)} rows from offset {offset}")

df = pd.DataFrame(all_data)
df.to_csv("arrests.csv", index=False)

print(f"Done! Downloaded {len(df)} rows total.")
print(df['arrest_date'].min(), "to", df['arrest_date'].max())