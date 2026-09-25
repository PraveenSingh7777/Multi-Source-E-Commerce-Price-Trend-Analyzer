# app.py
import streamlit as st
import plotly.express as px
from database import init_db, get_product_trend, get_deal_summary
from data_pipeline import CANONICAL_PRODUCTS, generate_pricing_history
import os

st.set_page_config(page_title="PricePulse | Trend Analyzer", layout="wide")

# Ensure database exists
if not os.path.exists("data/ecommerce.duckdb"):
    with st.spinner("Generating historical data and building DuckDB index..."):
        generate_pricing_history()
        init_db()

st.title("📊 Multi-Source E-Commerce Price Trend Analyzer")
st.caption("Entity Resolution via RapidFuzz | OLAP Analytics via DuckDB")

# Product selector
product_map = {prod["name"]: prod["id"] for prod in CANONICAL_PRODUCTS}
selected_product_name = st.selectbox("Select Target Product to Track", list(product_map.keys()))
selected_id = product_map[selected_product_name]

# Load analytical data
trend_df = get_product_trend(selected_id)
deal_info = get_deal_summary(selected_id)

if deal_info:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Best Current Store", deal_info["best_store"])
    col2.metric("Current Best Price", f"₹{deal_info['current_price']:,.2f}")
    col3.metric("All-Time Historic Low", f"₹{deal_info['all_time_low']:,.2f}")
    col4.metric("30-Day Mean Price", f"₹{deal_info['avg_price']:,.2f}")

st.divider()

# Time series plot
tab1, tab2 = st.tabs(["📈 Price Volatility Chart", "📋 Ingested Record Feed"])

with tab1:
    fig = px.line(
        trend_df,
        x="timestamp",
        y="price",
        color="store",
        line_shape="linear",
        title=f"Price Fluctuation History Across Retail Outlets: {selected_product_name}",
        labels={"timestamp": "Date", "price": "Price (INR)", "store": "Store Channel"},
    )
    fig.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.write("Cross-store matched raw listings extracted from DuckDB:")
    st.dataframe(trend_df, use_container_width=True)
