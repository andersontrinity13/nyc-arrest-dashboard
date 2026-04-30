# NYC Arrest Data Dashboard

A Streamlit data pipeline and interactive dashboard analyzing 50,000 NYPD arrest records from NYC Open Data.

## Project Goal
Analyze patterns in NYC arrest data to answer:
- What types of offenses are most frequently arrested for?
- How do arrest rates vary across NYC boroughs?
- Are there seasonal and weather-based trends in arrest data?
- What crimes increase in summer vs winter?

## Data Source
- **Dataset:** NYPD Arrests Data (Year to Date)
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrests-Data-Historic-/8h9b-rp9u)
- **Format:** JSON via Socrata API, converted to CSV
- **Size:** 50,000 records

## Project Files
| File | Purpose |
|------|---------|
| `download_data.py` | Pulls data from NYC Open Data API |
| `clean_data.py` | Cleans, transforms, and engineers features |
| `explore.py` | Initial data exploration and column audit |
| `app.py` | Streamlit dashboard with all visualizations |
| `arrests_clean.csv` | Cleaned dataset used by the app |

## How to Run
1. Install dependencies:
2. Download the data:
3. Clean the data:
4. Launch the dashboard:

## Built With
- Python 3.11
- Pandas
- Plotly
- Streamlit
- NYC Open Data Socrata API