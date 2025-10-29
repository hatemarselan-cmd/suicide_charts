
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Suicide Data Insights", layout="wide")

# --- Load Data
def load_data():
    df = pd.read_csv('master.csv')
    df.columns = df.columns.str.strip()
    if "gdp_for_year ($)" in df.columns:
        df["gdp_for_year ($)"] = df["gdp_for_year ($)"].astype(str).str.replace(",", "").astype(float)
    return df

df = load_data()

# --- Sidebar Page Selection
page = st.sidebar.radio("Pages", ["Home", "KPI's Dashboard", "Other Reports"])

# --- Shared Filters
years = ["All"] + sorted(df["year"].unique().tolist())
sexes = ["All"] + df["sex"].unique().tolist()
countries = ["All"] + df["country"].unique().tolist()

selected_years = st.sidebar.multiselect("Select Year(s)", options=years, default=["All"])
selected_sex = st.sidebar.multiselect("Select Sex", options=sexes, default=["All"])
selected_countries = st.sidebar.multiselect("Select Countries", options=countries, default=["All"])

# --- Handle "All" selections
filtered_years = df["year"].unique() if "All" in selected_years else selected_years
filtered_sex = df["sex"].unique() if "All" in selected_sex else selected_sex
filtered_countries = df["country"].unique() if "All" in selected_countries else selected_countries

df_filtered = df.query('year in @filtered_years & sex in @filtered_sex & country in @filtered_countries')

# --- Pages
if page == "Home":
    st.title("🌍 Global Suicide Analysis Dashboard")
    st.markdown("Welcome! Use the sidebar to filter the data and navigate between pages.")
    st.dataframe(df_filtered.head(10))
    
    with st.expander("📘 Click to view dataset column descriptions"):
        col_desc = {
            "country": "Name of the country.",
            "year": "Year of the recorded data.",
            "sex": "Gender category: male or female.",
            "age": "Age group in 5-year intervals.",
            "suicides_no": "Total number of suicides in that demographic group.",
            "population": "Population count for the same group.",
            "suicides/100k pop": "Suicides per 100,000 people.",
            "country-year": "Combined key of country and year.",
            "HDI for year": "Human Development Index for that year (if available).",
            "gdp_for_year ($)": "Total GDP for the year in US dollars.",
            "gdp_per_capita ($)": "GDP per person in US dollars.",
            "generation": "Generation label (e.g., Generation X, Boomers, etc.)."
        }
        desc_df = pd.DataFrame(list(col_desc.items()), columns=["Column Name", "Description"])
        st.table(desc_df)

elif page == "KPI's Dashboard":
    st.title("📊 Suicide KPIs Dashboard")

    # --- Global Trend Over Time
    df_yearly = df_filtered.groupby('year')['suicides/100k pop'].mean().reset_index()
    fig1 = px.line(df_yearly, x='year', y='suicides/100k pop', markers=True, color_discrete_sequence=['#FF6347'])
    st.plotly_chart(fig1, use_container_width=True)
    
       # --- Top 10 Countries by Total Suicides
    st.title("📊 Top 10 Countries by Total Suicides")
    top_countries = df.groupby('country')['suicides_no'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_co = px.bar(top_countries, x='country', y='suicides_no', color='country', text_auto=True)
    st.plotly_chart(fig_co, use_container_width=True)
    
    # --- Suicide by Sex
    st.title("📊 Suicide by Sex")
    df_sex = df_filtered.groupby('sex')['suicides/100k pop'].mean().reset_index()
    fig2 = px.bar(df_sex, x='sex', y='suicides/100k pop', color='sex',
                  text_auto='.2f', color_discrete_sequence=px.colors.qualitative.Vivid)
    st.plotly_chart(fig2, use_container_width=True)

    # --- Suicide by Age
    st.title("📊 Suicide by Age")
    df_age = df_filtered.groupby('age')['suicides/100k pop'].mean().reset_index()
    fig3 = px.bar(df_age, x='age', y='suicides/100k pop', color='age',
                  text_auto='.2f', color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig3, use_container_width=True)

    # --- Top 10 Countries by Suicide Rate
    st.title("📊 Top 10 Countries by Total Suicides Rate")
    df_country = df_filtered.groupby('country')['suicides/100k pop'].mean().reset_index().sort_values('suicides/100k pop', ascending=False).head(10)
    fig4 = px.bar(df_country, x='country', y='suicides/100k pop', color='country',
                  text_auto='.2f', color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(fig4, use_container_width=True)

elif page == "Other Reports":

    # --- Generation Analysis
    st.title("📊 Generation per suicides/100k pop ")
    df_gen = df_filtered.groupby('generation')['suicides/100k pop'].mean().reset_index().sort_values(by='suicides/100k pop', ascending=False)
    fig_gen = px.bar(df_gen, x='generation', y='suicides/100k pop', color='generation',
                     text_auto='.2f', color_discrete_sequence=px.colors.qualitative.T10)
    st.plotly_chart(fig_gen, use_container_width=True)
    
    
    st.title("📊 Share of Average Suicide Rate by Generation")
    gen_df_1 = df.groupby('generation')['suicides_no'].sum().reset_index()
    fig_gen_1 = px.pie(gen_df_1, names='generation', values='suicides_no',
                title='Total Suicides by Generation', hole=0.4)
    st.plotly_chart(fig_gen_1, use_container_width=True)
    
    # --- Heatmap: Year vs Sex
    st.title("📊 year & Sex for suicides/100k pop ")
    df_heat = df_filtered.groupby(['year', 'sex'])['suicides/100k pop'].mean().reset_index()
    fig_heat = px.density_heatmap(df_heat, x='year', y='sex', z='suicides/100k pop',
                                  color_continuous_scale='Viridis')
    st.plotly_chart(fig_heat, use_container_width=True)
