import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NYC Arrest Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Dark base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d0d;
    color: #f0ece4;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #2a2a2a;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 2px;
    color: #f0ece4;
}

/* KPI metric cards */
.kpi-card {
    background: linear-gradient(135deg, #1a1a1a 0%, #1f1f1f 100%);
    border: 1px solid #2e2e2e;
    border-left: 4px solid #e63946;
    border-radius: 4px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.kpi-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    color: #e63946;
    letter-spacing: 2px;
    line-height: 1;
}
.kpi-label {
    font-size: 0.72rem;
    color: #888;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* Section dividers */
.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    letter-spacing: 3px;
    color: #f0ece4;
    border-bottom: 2px solid #e63946;
    padding-bottom: 6px;
    margin-top: 32px;
    margin-bottom: 4px;
}

/* Weather card */
.weather-card {
    background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 20px;
    text-align: center;
}
.weather-temp {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    color: #60a5fa;
    letter-spacing: 2px;
}
.weather-desc {
    font-size: 0.85rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111;
    border-bottom: 2px solid #2a2a2a;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 2px;
    font-size: 1rem;
    color: #666;
    background: transparent;
    border: none;
    padding: 10px 22px;
}
.stTabs [aria-selected="true"] {
    color: #e63946 !important;
    border-bottom: 2px solid #e63946 !important;
    background: transparent !important;
}

/* Plotly chart backgrounds */
.js-plotly-plot { border-radius: 6px; }

/* Sidebar labels */
[data-testid="stSidebar"] label {
    color: #aaa !important;
    font-size: 0.78rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Expander */
[data-testid="stExpander"] {
    background: #111;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
}

/* Remove default padding top */
.block-container { padding-top: 1.5rem; }

/* Tag badge */
.badge {
    display: inline-block;
    background: #e63946;
    color: white;
    font-size: 0.7rem;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 2px;
    margin-left: 8px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ── DATA LOADING ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("arrests_clean.csv")
    df['arrest_date'] = pd.to_datetime(df['arrest_date'])
    return df

df = load_data()

# ── WEATHER API ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800)
def get_nyc_weather():
    """Fetch current NYC weather from Open-Meteo (free, no key required)."""
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            "?latitude=40.7128&longitude=-74.0060"
            "&current_weather=true"
            "&temperature_unit=fahrenheit"
            "&windspeed_unit=mph"
        )
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            cw = data["current_weather"]
            return {
                "temp_f": round(cw["temperature"], 1),
                "windspeed": round(cw["windspeed"], 1),
                "weathercode": cw["weathercode"],
                "is_day": cw.get("is_day", 1)
            }
    except Exception:
        pass
    return None

def weather_code_to_desc(code):
    mapping = {
        0: ("Clear Sky", "☀️"),
        1: ("Mainly Clear", "🌤️"), 2: ("Partly Cloudy", "⛅"), 3: ("Overcast", "☁️"),
        45: ("Foggy", "🌫️"), 48: ("Icy Fog", "🌫️"),
        51: ("Light Drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy Drizzle", "🌧️"),
        61: ("Light Rain", "🌧️"), 63: ("Rain", "🌧️"), 65: ("Heavy Rain", "🌧️"),
        71: ("Light Snow", "🌨️"), 73: ("Snow", "❄️"), 75: ("Heavy Snow", "❄️"),
        80: ("Rain Showers", "🌦️"), 81: ("Rain Showers", "🌧️"), 82: ("Violent Showers", "⛈️"),
        95: ("Thunderstorm", "⛈️"), 96: ("Thunderstorm+Hail", "⛈️"), 99: ("Heavy Thunderstorm", "⛈️"),
    }
    return mapping.get(code, ("Unknown", "🌡️"))

# ── PLOTLY THEME ──────────────────────────────────────────────────────────────
CHART_THEME = {
    "paper_bgcolor": "#141414",
    "plot_bgcolor": "#141414",
    "font": {"color": "#c9c3bb", "family": "DM Sans"},
    "xaxis": {"gridcolor": "#1f1f1f", "linecolor": "#2a2a2a"},
}
RED = "#e63946"
BLUE = "#457b9d"
ACCENT = "#f4a261"

def apply_theme(fig):
    fig.update_layout(**CHART_THEME, margin=dict(t=30, b=20, l=10, r=10))
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:\'Bebas Neue\',sans-serif;font-size:1.5rem;letter-spacing:3px;color:#e63946;margin-bottom:0">NYPD ARREST</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:\'Bebas Neue\',sans-serif;font-size:1.1rem;letter-spacing:2px;color:#888;margin-top:0">INTELLIGENCE DASHBOARD</p>', unsafe_allow_html=True)
    st.markdown("---")

    borough_options = ["All"] + sorted(df['borough_name'].dropna().unique().tolist())
    selected_boro = st.selectbox("Borough", borough_options)

    law_options = ["All"] + sorted(df['law_category'].dropna().unique().tolist())
    selected_law = st.selectbox("Law Category", law_options)

    if 'season' in df.columns:
        season_options = ["All"] + ['Winter', 'Spring', 'Summer', 'Fall']
        selected_season = st.selectbox("Season", season_options)
    else:
        selected_season = "All"

    st.markdown("---")

    # Live weather widget
    weather = get_nyc_weather()
    if weather:
        desc, icon = weather_code_to_desc(weather["weathercode"])
        st.markdown(f"""
        <div class="weather-card">
            <div style="font-size:2rem">{icon}</div>
            <div class="weather-temp">{weather['temp_f']}°F</div>
            <div class="weather-desc">{desc}</div>
            <div style="color:#6b7280;font-size:0.75rem;margin-top:8px">
                💨 {weather['windspeed']} mph · NYC Live
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Weather unavailable")

    st.markdown("---")
    st.markdown('<p style="color:#444;font-size:0.7rem;text-align:center">NYC Open Data · NYPD Arrests<br>Open-Meteo Weather API</p>', unsafe_allow_html=True)

# ── FILTER DATA ───────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_boro != "All":
    filtered = filtered[filtered['borough_name'] == selected_boro]
if selected_law != "All":
    filtered = filtered[filtered['law_category'] == selected_law]
if selected_season != "All" and 'season' in filtered.columns:
    filtered = filtered[filtered['season'] == selected_season]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<h1 style="font-size:3rem;letter-spacing:5px;margin-bottom:0">NYC ARREST DASHBOARD</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="color:#666;font-size:0.85rem;margin-top:4px">NYPD · 50,000 Records · iSchool IST 356 · Showing <span style="color:#e63946;font-weight:600">{len(filtered):,}</span> arrests</p>', unsafe_allow_html=True)

# ── KPI ROW ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(filtered):,}</div><div class="kpi-label">Total Arrests</div></div>', unsafe_allow_html=True)
with k2:
    top_boro = filtered['borough_name'].mode()[0] if len(filtered) > 0 else "N/A"
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{top_boro}</div><div class="kpi-label">Highest Borough</div></div>', unsafe_allow_html=True)
with k3:
    top_offense = filtered['ofns_desc'].mode()[0][:20] if len(filtered) > 0 else "N/A"
    st.markdown(f'<div class="kpi-card"><div class="kpi-value" style="font-size:1.3rem">{top_offense}</div><div class="kpi-label">Top Offense</div></div>', unsafe_allow_html=True)
with k4:
    if 'season' in filtered.columns and len(filtered) > 0:
        top_season = filtered['season'].mode()[0]
    else:
        top_season = "N/A"
    st.markdown(f'<div class="kpi-card"><div class="kpi-value">{top_season}</div><div class="kpi-label">Peak Season</div></div>', unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  OVERVIEW",
    "🗺️  ARREST MAP",
    "🌡️  WEATHER & SEASONS",
    "🔍  DEEP DIVE"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">TOP 10 OFFENSES</div>', unsafe_allow_html=True)
        top_offenses = filtered['ofns_desc'].value_counts().head(10).reset_index()
        top_offenses.columns = ['Offense', 'Count']
        fig1 = px.bar(top_offenses, x='Count', y='Offense', orientation='h',
                      color='Count', color_continuous_scale=[[0, '#2d0a0e'], [1, RED]])
        fig1.update_layout(**CHART_THEME, margin=dict(t=10, b=20, l=10, r=10),
                           coloraxis_showscale=False,
                           yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">ARRESTS BY BOROUGH</div>', unsafe_allow_html=True)
        boro_counts = filtered['borough_name'].value_counts().reset_index()
        boro_counts.columns = ['Borough', 'Count']
        fig2 = px.pie(boro_counts, names='Borough', values='Count',
                      color_discrete_sequence=['#e63946', '#457b9d', '#f4a261', '#2a9d8f', '#e9c46a'],
                      hole=0.45)
        fig2.update_layout(**CHART_THEME, margin=dict(t=10, b=10, l=10, r=10))
        fig2.update_traces(textfont_color='white')
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">LAW CATEGORY</div>', unsafe_allow_html=True)
        law_counts = filtered['law_category'].value_counts().reset_index()
        law_counts.columns = ['Category', 'Count']
        fig3 = px.bar(law_counts, x='Category', y='Count',
                      color='Category',
                      color_discrete_sequence=[RED, BLUE, ACCENT, '#2a9d8f'])
        fig3.update_layout(**CHART_THEME, showlegend=False, margin=dict(t=10, b=20, l=10, r=10))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">AGE GROUP</div>', unsafe_allow_html=True)
        age_counts = filtered['age_group'].value_counts().reset_index()
        age_counts.columns = ['Age Group', 'Count']
        fig4 = px.bar(age_counts, x='Age Group', y='Count',
                      color='Age Group',
                      color_discrete_sequence=[RED, BLUE, ACCENT, '#2a9d8f', '#e9c46a'])
        fig4.update_layout(**CHART_THEME, showlegend=False, margin=dict(t=10, b=20, l=10, r=10))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">ARRESTS OVER TIME</div>', unsafe_allow_html=True)
    monthly = filtered.groupby(filtered['arrest_date'].dt.to_period('M')).size().reset_index()
    monthly.columns = ['Month', 'Count']
    monthly['Month'] = monthly['Month'].astype(str)
    fig5 = px.line(monthly, x='Month', y='Count', markers=True,
                   color_discrete_sequence=[RED])
    fig5.update_traces(line_width=2.5, marker_size=6,
                       fill='tozeroy', fillcolor='rgba(230,57,70,0.08)')
    fig5.update_layout(**CHART_THEME, margin=dict(t=10, b=40, l=10, r=10),
                       xaxis_tickangle=-45)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown('<div class="section-header">ARRESTS BY RACE</div>', unsafe_allow_html=True)
    race_counts = filtered['perp_race'].value_counts().reset_index()
    race_counts.columns = ['Race', 'Count']
    fig6 = px.bar(race_counts, x='Race', y='Count', color='Race',
                  color_discrete_sequence=[RED, BLUE, ACCENT, '#2a9d8f', '#e9c46a', '#9b5de5', '#00bbf9'])
    fig6.update_layout(**CHART_THEME, showlegend=False, xaxis_tickangle=-30,
                       margin=dict(t=10, b=60, l=10, r=10))
    st.plotly_chart(fig6, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — MAP
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">ARREST LOCATIONS — NYC MAP</div>', unsafe_allow_html=True)

    map_df = filtered.dropna(subset=['latitude', 'longitude']).copy()
    map_df = map_df[(map_df['latitude'] != 0) & (map_df['longitude'] != 0)]
    map_df = map_df[(map_df['latitude'] > 40.4) & (map_df['latitude'] < 40.95)]
    map_df = map_df[(map_df['longitude'] > -74.3) & (map_df['longitude'] < -73.65)]

    if len(map_df) == 0:
        st.warning("No location data available for the current filters. Make sure arrests_clean.csv has 'latitude' and 'longitude' columns.")
    else:
        # Sample for performance if large
        sample_size = min(10000, len(map_df))
        map_sample = map_df.sample(sample_size, random_state=42) if len(map_df) > sample_size else map_df

        mcol1, mcol2 = st.columns([3, 1])
        with mcol2:
            map_type = st.radio("Map Style", ["Scatter", "Density Heatmap"], index=0)
            color_by = st.selectbox("Color Points By", ["borough_name", "law_category", "age_group"])
            st.caption(f"Plotting {len(map_sample):,} of {len(map_df):,} arrest locations")

        with mcol1:
            if map_type == "Scatter":
                fig_map = px.scatter_mapbox(
                    map_sample,
                    lat='latitude', lon='longitude',
                    color=color_by,
                    color_discrete_sequence=[RED, BLUE, ACCENT, '#2a9d8f', '#e9c46a'],
                    hover_data={'latitude': False, 'longitude': False,
                                'ofns_desc': True, 'borough_name': True,
                                'law_category': True},
                    zoom=10, height=580,
                    opacity=0.55,
                    size_max=6,
                )
            else:
                fig_map = px.density_mapbox(
                    map_sample,
                    lat='latitude', lon='longitude',
                    radius=8, zoom=10, height=580,
                    color_continuous_scale=[[0, 'rgba(0,0,0,0)'],
                                            [0.3, 'rgba(230,57,70,0.4)'],
                                            [1.0, 'rgba(230,57,70,1.0)']],
                )

            fig_map.update_layout(
                mapbox_style="carto-darkmatter",
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor="#141414",
                legend=dict(bgcolor='rgba(20,20,20,0.8)', bordercolor='#2a2a2a',
                            borderwidth=1, font=dict(color='#c9c3bb')),
            )
            st.plotly_chart(fig_map, use_container_width=True)

    # Borough heatmap grid
    st.markdown('<div class="section-header">ARREST DENSITY BY BOROUGH × OFFENSE</div>', unsafe_allow_html=True)
    top_offenses_list = filtered['ofns_desc'].value_counts().head(8).index.tolist()
    heatmap_df = filtered[filtered['ofns_desc'].isin(top_offenses_list)]
    pivot = heatmap_df.groupby(['borough_name', 'ofns_desc']).size().unstack(fill_value=0)
    fig_heat = px.imshow(pivot,
                         color_continuous_scale=[[0, '#0d0d0d'], [0.5, '#7a1921'], [1, RED]],
                         aspect='auto', height=300)
    fig_heat.update_layout(**CHART_THEME, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_heat, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — WEATHER & SEASONS
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    # Live weather correlation callout
    if weather:
        desc, icon = weather_code_to_desc(weather["weathercode"])
        temp = weather["temp_f"]
        if temp >= 75:
            insight = f"🔴 It's currently {temp}°F in NYC ({desc}). Historically, hot weather correlates with higher assault and drug arrest rates in the dataset."
        elif temp <= 35:
            insight = f"🔵 It's currently {temp}°F in NYC ({desc}). Cold weather periods show lower overall arrest volumes in the dataset."
        else:
            insight = f"🟡 It's currently {temp}°F in NYC ({desc}). Mild weather shows moderate and stable arrest patterns."
        st.info(insight)

    col5, col6 = st.columns(2)

    with col5:
        st.markdown('<div class="section-header">ARRESTS BY SEASON</div>', unsafe_allow_html=True)
        season_counts = filtered['season'].value_counts().reset_index()
        season_counts.columns = ['Season', 'Count']
        season_order = ['Winter', 'Spring', 'Summer', 'Fall']
        season_counts['Season'] = pd.Categorical(season_counts['Season'], categories=season_order, ordered=True)
        season_counts = season_counts.sort_values('Season')
        fig7 = px.bar(season_counts, x='Season', y='Count', color='Season',
                      color_discrete_map={
                          'Winter': '#85c1e9', 'Spring': '#82e0aa',
                          'Summer': '#f9e79f', 'Fall': '#f0b27a'
                      })
        fig7.update_layout(**CHART_THEME, showlegend=False, margin=dict(t=10, b=20, l=10, r=10))
        st.plotly_chart(fig7, use_container_width=True)

    with col6:
        st.markdown('<div class="section-header">HOT vs COLD vs MILD</div>', unsafe_allow_html=True)
        temp_counts = filtered['temp_category'].value_counts().reset_index()
        temp_counts.columns = ['Temp Category', 'Count']
        fig8 = px.pie(temp_counts, names='Temp Category', values='Count',
                      color_discrete_map={
                          'Hot (Jun-Sep)': RED,
                          'Cold (Dec-Mar)': '#85c1e9',
                          'Mild (Apr-May, Oct-Nov)': '#82e0aa'
                      }, hole=0.4)
        fig8.update_layout(**CHART_THEME, margin=dict(t=10, b=10, l=10, r=10))
        fig8.update_traces(textfont_color='white')
        st.plotly_chart(fig8, use_container_width=True)

    st.markdown('<div class="section-header">🔥 SUMMER vs ❄️ WINTER — TOP OFFENSES</div>', unsafe_allow_html=True)
    summer = filtered[filtered['season'] == 'Summer']['ofns_desc'].value_counts().head(10).reset_index()
    summer.columns = ['Offense', 'Count']
    summer['Season'] = 'Summer'
    winter = filtered[filtered['season'] == 'Winter']['ofns_desc'].value_counts().head(10).reset_index()
    winter.columns = ['Offense', 'Count']
    winter['Season'] = 'Winter'
    combined = pd.concat([summer, winter])
    fig9 = px.bar(combined, x='Count', y='Offense', color='Season', orientation='h',
                  barmode='group',
                  color_discrete_map={'Summer': RED, 'Winter': '#5dade2'})
    fig9.update_layout(**CHART_THEME, yaxis={'categoryorder': 'total ascending'},
                       margin=dict(t=10, b=20, l=10, r=30))
    st.plotly_chart(fig9, use_container_width=True)

    st.markdown('<div class="section-header">MONTHLY ARREST VOLUME BY SEASON</div>', unsafe_allow_html=True)
    monthly2 = filtered.copy()
    monthly2['month_num'] = monthly2['arrest_date'].dt.month
    monthly2['month_name'] = monthly2['arrest_date'].dt.strftime('%B')
    monthly_counts = monthly2.groupby(['month_num', 'month_name']).size().reset_index()
    monthly_counts.columns = ['month_num', 'Month', 'Count']
    monthly_counts = monthly_counts.sort_values('month_num')

    def month_to_season(m):
        if m in [12, 1, 2]: return 'Winter'
        elif m in [3, 4, 5]: return 'Spring'
        elif m in [6, 7, 8]: return 'Summer'
        else: return 'Fall'

    monthly_counts['Season'] = monthly_counts['month_num'].apply(month_to_season)
    fig10 = px.bar(monthly_counts, x='Month', y='Count', color='Season',
                   color_discrete_map={
                       'Winter': '#85c1e9', 'Spring': '#82e0aa',
                       'Summer': '#f9e79f', 'Fall': '#f0b27a'
                   },
                   category_orders={'Month': ['January','February','March','April',
                                              'May','June','July','August',
                                              'September','October','November','December']})
    fig10.update_layout(**CHART_THEME, margin=dict(t=10, b=40, l=10, r=10))
    st.plotly_chart(fig10, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — DEEP DIVE
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">GENDER BREAKDOWN</div>', unsafe_allow_html=True)
    if 'perp_sex' in filtered.columns:
        gender_counts = filtered['perp_sex'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        fig_g = px.bar(gender_counts, x='Gender', y='Count', color='Gender',
                       color_discrete_sequence=[RED, BLUE, ACCENT])
        fig_g.update_layout(**CHART_THEME, showlegend=False, margin=dict(t=10, b=20, l=10, r=10))
        st.plotly_chart(fig_g, use_container_width=True)

    st.markdown('<div class="section-header">ARREST TYPE OVER TIME</div>', unsafe_allow_html=True)
    if 'arrest_boro' in filtered.columns or 'borough_name' in filtered.columns:
        boro_col = 'borough_name' if 'borough_name' in filtered.columns else 'arrest_boro'
        monthly_boro = filtered.copy()
        monthly_boro['YearMonth'] = monthly_boro['arrest_date'].dt.to_period('M').astype(str)
        boro_time = monthly_boro.groupby(['YearMonth', boro_col]).size().reset_index()
        boro_time.columns = ['YearMonth', 'Borough', 'Count']
        fig_bt = px.line(boro_time, x='YearMonth', y='Count', color='Borough',
                         color_discrete_sequence=[RED, BLUE, ACCENT, '#2a9d8f', '#e9c46a'])
        fig_bt.update_layout(**CHART_THEME, xaxis_tickangle=-45,
                             margin=dict(t=10, b=60, l=10, r=10))
        st.plotly_chart(fig_bt, use_container_width=True)

    st.markdown('<div class="section-header">OFFENSE × AGE GROUP HEATMAP</div>', unsafe_allow_html=True)
    top10 = filtered['ofns_desc'].value_counts().head(10).index
    heat2 = filtered[filtered['ofns_desc'].isin(top10)]
    pivot2 = heat2.groupby(['age_group', 'ofns_desc']).size().unstack(fill_value=0)
    fig_h2 = px.imshow(pivot2,
                       color_continuous_scale=[[0, '#0d0d0d'], [0.5, '#7a1921'], [1, RED]],
                       aspect='auto', height=280)
    fig_h2.update_layout(**CHART_THEME, margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_h2, use_container_width=True)

    with st.expander("📋 VIEW RAW DATA SAMPLE (first 100 rows)"):
        st.dataframe(
            filtered.head(100).style.set_properties(**{
                'background-color': '#141414',
                'color': '#c9c3bb',
                'border': '1px solid #2a2a2a'
            }),
            use_container_width=True
        )
