# NYC Arrest Data Dashboard

A Streamlit data pipeline and interactive dashboard analyzing 50,000 NYPD arrest records from NYC Open Data.

## Project Goal
Analyze patterns in NYC arrest data to answer:
- What types of offenses are most frequently arrested for?
- How do arrest rates vary across NYC boroughs?
- Are there seasonal and weather-based trends in arrest data?
- What crimes increase in summer vs winter?

## Data Sources & APIs
- **Dataset:** NYPD Arrests Data (Year to Date)
- **Source:** [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/NYPD-Arrests-Data-Historic-/8h9b-rp9u)
- **Format:** JSON via Socrata API, converted to CSV
- **Size:** 50,000 records
- **Live Weather:** [Open-Meteo API](https://open-meteo.com/) — free, no key required

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
```bash
pip install pandas streamlit plotly requests
```
2. Download the data:
```bash
python download_data.py
```
3. Clean the data:
```bash
python clean_data.py
```
4. Launch the dashboard:
```bash
streamlit run app.py
```

## Built With
- Python 3.11
- Pandas
- Plotly
- Streamlit
- [NYC Open Data Socrata API](https://dev.socrata.com/)
- [Open-Meteo Weather API](https://open-meteo.com/)

## Course
IST 356 — Programming Techniques for Data Analytics
Syracuse University iSchool