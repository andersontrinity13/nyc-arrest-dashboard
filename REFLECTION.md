# Project Reflection

## IST 356 — Final Project
**Trinity Anderson | Syracuse University iSchool**

## Project Overview
For this project I built a full ETL pipeline and interactive Streamlit dashboard
analyzing 50,000 NYPD arrest records from NYC Open Data. The goal was to uncover
patterns in arrest data by borough, offense type, demographics, season, and weather.

## Design Decisions
- I chose NYC arrest data because of my interest in federal law enforcement and
  public safety analytics.
- I used the Socrata API to extract data programmatically rather than a static
  download, which gave me real ETL experience.
- I added a live weather API (Open-Meteo) to correlate current NYC conditions with
  historical arrest patterns — this was not required but added real analytical value.
- I separated the pipeline into three modules: download_data.py, clean_data.py,
  and app.py to keep responsibilities clean and modular.

## Challenges
- The raw dataset had inconsistent borough codes that needed to be mapped to full
  names during the cleaning phase.
- Plotly chart theming caused a duplicate keyword argument error when passing a
  shared theme dictionary — I fixed this by removing the conflicting yaxis key.
- Getting the scatter mapbox to filter out bad coordinates (zeros and out-of-range
  values) required adding boundary checks on latitude and longitude.
- Managing Python environment conflicts with packages took significant debugging
  time early in the semester.

## Learning Outcomes
- Gained hands-on experience building a real ETL pipeline from an external API
  to a cleaned dataset to a deployed Streamlit app.
- Learned how to integrate a live third-party REST API (Open-Meteo) into a
  Streamlit application with caching to avoid excessive calls.
- Improved my understanding of Pandas transformations including groupby, merge,
  pivot, and feature engineering (season, temp_category columns).
- Learned how to use Plotly Express for interactive data visualization and how
  to apply consistent theming across multiple chart types.
- Strengthened my GitHub workflow including committing, pushing, and maintaining
  a well-documented repository.

## What I Would Do Next
- Add a geographic map plotting every arrest by latitude and longitude on an
  interactive NYC map.
- Pull in historical weather data from an API to more precisely correlate
  temperature with crime rates over time.
- Polish the dashboard further and deploy it publicly via Streamlit Cloud.