import streamlit as st
import pandas as pd
import plotly.express as px
import os

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="PhonePe Dashboard", layout="wide")
st.title("📊 PhonePe Transaction Insights Dashboard")

# -----------------------------
# LOAD DATA (CLOUD SAFE)
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, "final_df.csv")

df = pd.read_csv(file_path)

# -----------------------------
# DATA CLEANING
# -----------------------------
df["agg_amount"] = pd.to_numeric(df["agg_amount"], errors="coerce").fillna(0)
df["agg_count"] = pd.to_numeric(df["agg_count"], errors="coerce").fillna(0)

# -----------------------------
# STATE DECODING (ONE-HOT FIX)
# -----------------------------
state_cols = [c for c in df.columns if c.startswith("state_")]

def get_state(row):
    for col in state_cols:
        if row[col] == 1:
            return col.replace("state_", "").replace("-", " ").title()
    return "Unknown"

df["State"] = df.apply(get_state, axis=1)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

year_filter = st.sidebar.multiselect(
    "Year", sorted(df["year"].unique()), default=df["year"].unique()
)

quarter_filter = st.sidebar.multiselect(
    "Quarter", sorted(df["quarter"].unique()), default=df["quarter"].unique()
)

state_filter = st.sidebar.multiselect(
    "State", sorted(df["State"].unique()), default=df["State"].unique()
)

df = df[
    (df["year"].isin(year_filter)) &
    (df["quarter"].isin(quarter_filter)) &
    (df["State"].isin(state_filter))
]

# -----------------------------
# KPI METRICS
# -----------------------------
st.subheader("📌 Key Performance Indicators")

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Amount", f"{df['agg_amount'].sum():,.0f}")
col2.metric("🔢 Total Transactions", f"{df['agg_count'].sum():,.0f}")
col3.metric("📊 Avg Transaction Value", f"{df['agg_amount'].mean():,.2f}")

# -----------------------------
# YEAR TREND
# -----------------------------
st.subheader("📈 Yearly Trend")

year_df = df.groupby("year")["agg_amount"].sum().reset_index()

fig1 = px.line(year_df, x="year", y="agg_amount", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# QUARTER ANALYSIS
# -----------------------------
st.subheader("📊 Quarter Analysis")

quarter_df = df.groupby("quarter")["agg_amount"].sum().reset_index()

fig2 = px.bar(quarter_df, x="quarter", y="agg_amount", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# STATE ANALYSIS
# -----------------------------
st.subheader("🗺️ State-wise Performance")

state_df = df.groupby("State")["agg_amount"].sum().reset_index()
state_df = state_df.sort_values("agg_amount", ascending=False)

fig3 = px.bar(state_df.head(15), x="State", y="agg_amount", text_auto=True)
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# INSIGHTS ENGINE
# -----------------------------
st.subheader("🧠 AI-Style Insights")

top_state = state_df.iloc[0]["State"]
top_value = state_df.iloc[0]["agg_amount"]

best_year = year_df.loc[year_df["agg_amount"].idxmax(), "year"]

st.markdown(f"""
- 🔥 **Top State:** {top_state}  
- 💰 **Highest Transaction Year:** {best_year}  
- 📊 **Total Transaction Value:** {df['agg_amount'].sum():,.0f}  
- 🚀 **Top State Contribution:** {top_value:,.0f}  
""")

# -----------------------------
# DOWNLOAD DATA
# -----------------------------
st.subheader("📥 Download Data")

st.download_button(
    "Download Filtered Data",
    data=df.to_csv(index=False),
    file_name="phonepe_filtered_data.csv",
    mime="text/csv"
)

# -----------------------------
# RAW DATA
# -----------------------------
with st.expander("📂 View Raw Data"):
    st.dataframe(df)
