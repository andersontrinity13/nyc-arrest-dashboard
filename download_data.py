import requests
import pandas as pd

print("Downloading NYC Arrest data...")

url = "https://data.cityofnewyork.us/resource/uip8-fykc.json"

params = {
    "$limit": 50000,
    "$offset": 0
}

response = requests.get(url, params=params)
data = response.json()

df = pd.DataFrame(data)
df.to_csv("arrests.csv", index=False)

print(f"Done! Downloaded {len(df)} rows.")
print(df.head())