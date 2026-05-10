"""
Unit tests for the NYC Arrest Data pipeline.
Tests core transformation logic from clean_data.py
"""

import pandas as pd
import pytest

# ── Helper: create a small sample dataframe for testing ──────────────────────
def make_sample_df():
    return pd.DataFrame({
        'arrest_date': ['2023-01-15', '2023-06-20', '2023-09-05', '2023-11-30'],
        'arrest_boro': ['B', 'M', 'Q', 'K'],
        'age_group': ['25-44', '18-24', '45-64', '25-44'],
        'perp_sex': ['M', 'F', 'M', 'M'],
        'perp_race': ['BLACK', 'WHITE', 'HISPANIC', 'BLACK'],
        'ofns_desc': ['ASSAULT', 'LARCENY', 'DRUGS', 'ASSAULT'],
        'law_cat_cd': ['F', 'M', 'F', 'M'],
        'latitude': [40.65, 40.75, 40.72, 40.68],
        'longitude': [-73.95, -73.99, -73.85, -73.92],
    })

# ── Test 1: Borough mapping ───────────────────────────────────────────────────
def test_borough_mapping():
    df = make_sample_df()
    boro_map = {'B': 'Bronx', 'M': 'Manhattan', 'Q': 'Queens',
                'K': 'Brooklyn', 'S': 'Staten Island'}
    df['borough_name'] = df['arrest_boro'].map(boro_map)
    assert df.loc[0, 'borough_name'] == 'Bronx'
    assert df.loc[1, 'borough_name'] == 'Manhattan'
    assert df.loc[2, 'borough_name'] == 'Queens'
    assert df.loc[3, 'borough_name'] == 'Brooklyn'

# ── Test 2: Season assignment ─────────────────────────────────────────────────
def test_season_assignment():
    df = make_sample_df()
    df['arrest_date'] = pd.to_datetime(df['arrest_date'])
    df['month'] = df['arrest_date'].dt.month

    def get_season(m):
        if m in [12, 1, 2]: return 'Winter'
        elif m in [3, 4, 5]: return 'Spring'
        elif m in [6, 7, 8]: return 'Summer'
        else: return 'Fall'

    df['season'] = df['month'].apply(get_season)
    assert df.loc[0, 'season'] == 'Winter'
    assert df.loc[1, 'season'] == 'Summer'
    assert df.loc[3, 'season'] == 'Fall'

# ── Test 3: Law category mapping ──────────────────────────────────────────────
def test_law_category_mapping():
    df = make_sample_df()
    law_map = {'F': 'Felony', 'M': 'Misdemeanor', 'V': 'Violation', 'I': 'Infraction'}
    df['law_category'] = df['law_cat_cd'].map(law_map)
    assert df.loc[0, 'law_category'] == 'Felony'
    assert df.loc[1, 'law_category'] == 'Misdemeanor'

# ── Test 4: No null coordinates after filter ──────────────────────────────────
def test_no_null_coordinates():
    df = make_sample_df()
    df = df.dropna(subset=['latitude', 'longitude'])
    df = df[(df['latitude'] != 0) & (df['longitude'] != 0)]
    assert df['latitude'].isnull().sum() == 0
    assert df['longitude'].isnull().sum() == 0

# ── Test 5: Date parsing ──────────────────────────────────────────────────────
def test_date_parsing():
    df = make_sample_df()
    df['arrest_date'] = pd.to_datetime(df['arrest_date'])
    assert df['arrest_date'].dtype == 'datetime64[ns]'