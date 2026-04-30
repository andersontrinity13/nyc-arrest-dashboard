import pandas as pd

df = pd.read_csv("arrests.csv")

print("Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())
print("\nData Types:")
print(df.dtypes)
print("\nFirst 3 rows:")
print(df.head(3))
print("\nMissing values per column:")
print(df.isnull().sum())