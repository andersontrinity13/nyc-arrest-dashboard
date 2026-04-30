import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NYC Arrest Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("arrests_clean.csv")
    df['arrest_date'] = pd.to_datetime(df['arrest_date'])
    return df

df = load_data()

# ---- HEADER ----
st.title("🚔 NYC Arrest Data Dashboard")
st.markdown("Analyzing 50,000 NYPD arrest records from NYC Open Data.")

# ---- SIDEBAR FILTERS ----
st.sidebar.header("Filter Data")

borough_options = ["All"] + sorted(df['borough_name'].dropna().unique().tolist())
selected_boro = st.sidebar.selectbox("Borough", borough_options)

law_options = ["All"] + sorted(df['law_category'].dropna().unique().tolist())
selected_law = st.sidebar.selectbox("Law Category", law_options)

# Apply filters
filtered = df.copy()
if selected_boro != "All":
    filtered = filtered[filtered['borough_name'] == selected_boro]
if selected_law != "All":
    filtered = filtered[filtered['law_category'] == selected_law]

st.markdown(f"**Showing {len(filtered):,} arrests**")

# ---- ROW 1: Top Offenses + Borough Breakdown ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Offense Types")
    top_offenses = filtered['ofns_desc'].value_counts().head(10).reset_index()
    top_offenses.columns = ['Offense', 'Count']
    fig1 = px.bar(top_offenses, x='Count', y='Offense', orientation='h',
                  color='Count', color_continuous_scale='Reds')
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Arrests by Borough")
    boro_counts = filtered['borough_name'].value_counts().reset_index()
    boro_counts.columns = ['Borough', 'Count']
    fig2 = px.pie(boro_counts, names='Borough', values='Count',
                  color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig2, use_container_width=True)

# ---- ROW 2: Law Category + Age Group ----
col3, col4 = st.columns(2)

with col3:
    st.subheader("Arrests by Law Category")
    law_counts = filtered['law_category'].value_counts().reset_index()
    law_counts.columns = ['Category', 'Count']
    fig3 = px.bar(law_counts, x='Category', y='Count',
                  color='Category', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_layout(showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Arrests by Age Group")
    age_counts = filtered['age_group'].value_counts().reset_index()
    age_counts.columns = ['Age Group', 'Count']
    fig4 = px.bar(age_counts, x='Age Group', y='Count',
                  color='Age Group', color_discrete_sequence=px.colors.qualitative.Bold)
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

# ---- ROW 3: Arrests Over Time ----
st.subheader("Arrests Over Time (by Month)")
monthly = filtered.groupby(filtered['arrest_date'].dt.to_period('M')).size().reset_index()
monthly.columns = ['Month', 'Count']
monthly['Month'] = monthly['Month'].astype(str)
fig5 = px.line(monthly, x='Month', y='Count', markers=True,
               color_discrete_sequence=['#e63946'])
fig5.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig5, use_container_width=True)

# ---- ROW 4: Race breakdown ----
st.subheader("Arrests by Race")
race_counts = filtered['perp_race'].value_counts().reset_index()
race_counts.columns = ['Race', 'Count']
fig6 = px.bar(race_counts, x='Race', y='Count',
              color='Race', color_discrete_sequence=px.colors.qualitative.Safe)
fig6.update_layout(showlegend=False, xaxis_tickangle=-30)
st.plotly_chart(fig6, use_container_width=True)

# ---- SEASON & WEATHER ANALYSIS ----
st.markdown("---")
st.header("Seasonal & Weather-Based Crime Patterns")

col5, col6 = st.columns(2)

with col5:
    st.subheader("Total Arrests by Season")
    season_counts = filtered['season'].value_counts().reset_index()
    season_counts.columns = ['Season', 'Count']
    season_order = ['Winter', 'Spring', 'Summer', 'Fall']
    season_counts['Season'] = pd.Categorical(season_counts['Season'], categories=season_order, ordered=True)
    season_counts = season_counts.sort_values('Season')
    fig7 = px.bar(season_counts, x='Season', y='Count',
                  color='Season',
                  color_discrete_map={
                      'Winter': '#aed6f1',
                      'Spring': '#a9dfbf',
                      'Summer': '#f9e79f',
                      'Fall': '#f0b27a'
                  })
    fig7.update_layout(showlegend=False)
    st.plotly_chart(fig7, use_container_width=True)

with col6:
    st.subheader("Arrests: Hot vs Cold vs Mild Weather")
    temp_counts = filtered['temp_category'].value_counts().reset_index()
    temp_counts.columns = ['Temp Category', 'Count']
    fig8 = px.pie(temp_counts, names='Temp Category', values='Count',
                  color_discrete_map={
                      'Hot (Jun-Sep)': '#e74c3c',
                      'Cold (Dec-Mar)': '#85c1e9',
                      'Mild (Apr-May, Oct-Nov)': '#a9dfbf'
                  })
    st.plotly_chart(fig8, use_container_width=True)

# Which offenses spike in summer vs winter
st.subheader("🔥 Top Offenses in Summer vs ❄️ Winter")

summer = filtered[filtered['season'] == 'Summer']['ofns_desc'].value_counts().head(10).reset_index()
summer.columns = ['Offense', 'Count']
summer['Season'] = 'Summer'

winter = filtered[filtered['season'] == 'Winter']['ofns_desc'].value_counts().head(10).reset_index()
winter.columns = ['Offense', 'Count']
winter['Season'] = 'Winter'

combined = pd.concat([summer, winter])
fig9 = px.bar(combined, x='Count', y='Offense', color='Season',
              orientation='h', barmode='group',
              color_discrete_map={'Summer': '#e74c3c', 'Winter': '#5dade2'})
fig9.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig9, use_container_width=True)

# Monthly arrest trend with season color
st.subheader("Monthly Arrest Volume (Colored by Season)")
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
                   'Winter': '#aed6f1',
                   'Spring': '#a9dfbf',
                   'Summer': '#f9e79f',
                   'Fall': '#f0b27a'
               },
               category_orders={'Month': ['January','February','March','April',
                                           'May','June','July','August',
                                           'September','October','November','December']})
st.plotly_chart(fig10, use_container_width=True)

# ---- RAW DATA ----
with st.expander("View Raw Data Sample"):
    st.dataframe(filtered.head(100))