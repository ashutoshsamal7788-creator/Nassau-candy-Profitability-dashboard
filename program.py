import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Nassau Candy Profitability Dashboard", layout="wide")
st.title("🍬 Nassau Candy Distributor - Profitability & Margin Performance")

# 2. Load and Clean Data (Step-by-Step Methodology)
@st.cache_data
def load_clean_data():
    df = pd.read_csv("nassau_candy_sales.csv")
    
    # Data Cleaning & Validation (Image 1000053313.jpg)
    df = df[(df['Sales'] > 0) & (df['Gross Profit'] != 0)] # Remove zero-sales / invalid records
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Division'] = df['Division'].str.strip() # Standardize labels
    
    # KPI Calculations (Image 1000053314.jpg)
    df['Gross Margin (%)'] = (df['Gross Profit'] / df['Sales']) * 100
    df['Profit per Unit'] = df['Gross Profit'] / df['Units']
    
    return df

df = load_clean_data()

# 3. Sidebar Filters (User Capabilities - Image 1000053315.jpg)
st.sidebar.header("🔍 Filter Options")

# Date range filter
min_date, max_date = df['Order Date'].min().date(), df['Order Date'].max().date()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Division filter
divisions = df['Division'].unique()
selected_divisions = st.sidebar.multiselect("Select Product Division", divisions, default=list(divisions))

# Margin threshold slider
margin_threshold = st.sidebar.slider("Highlight Profit Margin Lower Than (%)", 0, 100, 20)

# Filter the main dataframe based on user selections
filtered_df = df[
    (df['Order Date'].dt.date >= start_date) & 
    (df['Order Date'].dt.date <= end_date) & 
    (df['Division'].isin(selected_divisions))
]

# 4. Top-Level Metric Tiles (KPIs)
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Gross Profit'].sum()
avg_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales Revenue", f"${total_sales:,.2f}")
col2.metric("Total Gross Profit", f"${total_profit:,.2f}")
col3.metric("Overall Gross Margin", f"{avg_margin:.2f}%")

st.markdown("---")

# 5. Dashboard Modules (Image 1000053315.jpg)
tab1, tab2, tab3 = st.tabs(["📊 Profitability Leaderboard", "🏢 Division Performance", "⚠️ Cost & Margin Risk"])

with tab1:
    st.subheader("Product-Level Margin Leaderboard")
    # Aggregate data by product
    prod_perf = filtered_df.groupby("Product Name").agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Gross Profit", "sum"),
        Total_Units=("Units", "sum")
    ).reset_index()
    prod_perf['Gross Margin (%)'] = (prod_perf['Total_Profit'] / prod_perf['Total_Sales']) * 100
    prod_perf = prod_perf.sort_values(by="Gross Margin (%)", ascending=False)
    
    # Plotly Chart
    fig1 = px.bar(prod_perf, x="Gross Margin (%)", y="Product Name", orientation='h',
                  title="Products Ranked by Gross Margin %", color="Gross Margin (%)",
                  color_continuous_scale="Viridis")
    st.plotly_chart(fig1, use_container_width=True)
    st.dataframe(prod_perf.style.format({"Total_Sales": "${:,.2f}", "Total_Profit": "${:,.2f}", "Gross Margin (%)": "{:.2f}%"}))

with tab2:
    st.subheader("Division Performance & Volume Imbalance")
    div_perf = filtered_df.groupby("Division").agg(
        Revenue=("Sales", "sum"),
        Profit=("Gross Profit", "sum")
    ).reset_index()
    
    fig2 = px.barmode = 'group'
    fig2 = px.bar(div_perf, x="Division", y=["Revenue", "Profit"], title="Revenue vs Profit Comparison", barmode="group")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.subheader("Cost Structure Diagnostics & Margin Risk")
    # Cost vs Sales scatter analysis
    fig3 = px.scatter(filtered_df, x="Cost", y="Sales", color="Division", size="Units",
                      hover_data=["Product Name"], title="Cost vs Sales Scatter Plot (Detecting Pricing Inefficiencies)")
    st.plotly_chart(fig3, use_container_width=True)
    
    # Flag products below user defined margin threshold
    risk_products = prod_perf[prod_perf['Gross Margin (%)'] < margin_threshold]
    st.warning(f"⚠️ Flagged Products with Profit Margin below {margin_threshold}%:")
    if not risk_products.empty:
        st.dataframe(risk_products[["Product Name", "Gross Margin (%)"]])
    else:
        st.success("No products are tracking under the risk margin threshold!")