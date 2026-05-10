"""
explore.py
Quick audit of the raw arrests.csv right after download.
Run this before clean_data.py to understand what you're working with —
column names, data types, missing values, and a sample of the raw data.
This script doesn't modify anything, it's purely for exploration.
"""

import pandas as pd

df = pd.read_csv("arrests.csv")

# Basic shape check — how many rows and columns came in from the API
print("Shape:", df.shape)

# Full column list so we know what fields are available to keep or drop
print("\nColumns:")
print(df.columns.tolist())

# Check data types — important for catching dates stored as strings
# and numeric fields that came in as objects
print("\nData Types:")
print(df.dtypes)

# Quick sanity check on the first few rows to confirm data looks right
print("\nFirst 3 rows:")
print(df.head(3))

# Count missing values per column — helps decide what to drop vs fill
# in the cleaning step
print("\nMissing values per column:")
print(df.isnull().sum())
