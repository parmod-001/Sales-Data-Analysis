import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path



st.set_page_config(
    page_title="Sales Data Analysis",
    page_icon="📊",
    layout="wide"
)



st.markdown("""
<style>
    .main-title {
        font-size: 38px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        font-size: 16px;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background-color: #f0f4f8;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #d9e2ec;
    }
</style>
""", unsafe_allow_html=True)




st.markdown(
    '<div class="main-title">📊 Sales Data Analysis Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Sales Performance | Business Insights | Data Analytics</div>',
    unsafe_allow_html=True
)

st.divider()




@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    required_columns = [
        "Order_ID",
        "Order_Date",
        "Region",
        "Product",
        "Category",
        "Quantity",
        "Unit_Price",
        "Sales"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    data["Order_Date"] = pd.to_datetime(
        data["Order_Date"],
        errors="coerce"
    )

    for col in ["Quantity", "Unit_Price", "Sales"]:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    data = data.dropna(
        subset=[
            "Order_Date",
            "Quantity",
            "Unit_Price",
            "Sales"
        ]
    )

    data["Region"] = data["Region"].fillna("Unknown")
    data["Product"] = data["Product"].fillna("Unknown")
    data["Category"] = data["Category"].fillna("Unknown")

    data = data[
        (data["Quantity"] > 0) &
        (data["Unit_Price"] > 0) &
        (data["Sales"] >= 0)
    ].copy()

    data["Year"] = data["Order_Date"].dt.year
    data["Month"] = data["Order_Date"].dt.month
    data["Year_Month"] = data["Order_Date"].dt.to_period("M").astype(str)

    return data


# Find the dataset
BASE_DIR = Path(__file__).resolve().parent

candidate_dirs = [
    BASE_DIR / "data",
    BASE_DIR / "Data",
    BASE_DIR,
]

possible_files = []
for directory in candidate_dirs:
    for filename in ["cleaned_sales_data.csv", "sales_data.csv"]:
        candidate = directory / filename
        if candidate.exists():
            possible_files.append(candidate)

dataset_path = possible_files[0] if possible_files else None


# ==========================================
# DATASET UPLOAD
# ==========================================

with st.sidebar:
    st.header("⚙️ Dashboard Controls")

    uploaded_file = st.file_uploader(
        "Upload Sales CSV (optional)",
        type=["csv"]
    )

    st.caption(
        "By default, the app loads the CSV from your data folder."
    )


# ==========================================
# HANDLE DATA
# ==========================================

try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)

    elif dataset_path is not None:
        df = load_data(str(dataset_path))

    else:
        st.error(
            "Sales dataset not found. Please upload a CSV file "
            "or place sales_data.csv inside the data folder."
        )
        st.stop()

except Exception as error:
    st.error(f"Unable to load dataset: {error}")
    st.stop()


if df.empty:
    st.error("The dataset contains no valid sales records.")
    st.stop()


# ==========================================
# SIDEBAR FILTERS
# ==========================================

with st.sidebar:
    st.subheader("🔎 Filters")

    available_years = sorted(
        df["Year"].dropna().unique().tolist()
    )

    selected_years = st.multiselect(
        "Select Year",
        options=available_years,
        default=available_years
    )

    min_order_date = df["Order_Date"].min().date()
    max_order_date = df["Order_Date"].max().date()
    selected_date_range = st.date_input(
        "Order date range",
        value=(min_order_date, max_order_date),
        min_value=min_order_date,
        max_value=max_order_date
    )

    available_regions = sorted(
        df["Region"].unique().tolist()
    )

    selected_regions = st.multiselect(
        "Select Region",
        options=available_regions,
        default=available_regions
    )

    available_categories = sorted(
        df["Category"].unique().tolist()
    )

    selected_categories = st.multiselect(
        "Select Category",
        options=available_categories,
        default=available_categories
    )

    st.caption("Tip: use the filters to narrow the dashboard to specific years or business segments.")

if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
else:
    start_date = end_date = selected_date_range[0]

filtered_df = df[
    df["Year"].isin(selected_years) &
    (df["Order_Date"] >= pd.Timestamp(start_date)) &
    (df["Order_Date"] < pd.Timestamp(end_date) + pd.Timedelta(days=1)) &
    df["Region"].isin(selected_regions) &
    df["Category"].isin(selected_categories)
].copy()

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ==========================================
# KEY PERFORMANCE INDICATORS
# ==========================================

st.subheader("📌 Key Performance Indicators")

total_sales = filtered_df["Sales"].sum()
total_orders = filtered_df["Order_ID"].nunique()
total_quantity = filtered_df["Quantity"].sum()
average_order_value = total_sales / total_orders if total_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"₹{total_sales:,.0f}")
col2.metric("🧾 Total Orders", f"{total_orders:,}")
col3.metric("📦 Units Sold", f"{total_quantity:,.0f}")
col4.metric("🛒 Average Order Value", f"₹{average_order_value:,.2f}")

st.divider()

# ==========================================
# EXPLORATION TABS
# ==========================================

monthly_sales = (
    filtered_df.groupby("Year_Month", as_index=False)["Sales"]
    .sum()
    .sort_values("Year_Month")
)

region_sales = (
    filtered_df.groupby("Region", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

product_sales = (
    filtered_df.groupby("Product", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

category_sales = (
    filtered_df.groupby("Category", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

top_5_products = (
    product_sales.head(5)
)

overview_tab, region_tab, product_tab, forecast_tab, data_tab = st.tabs([
    "Overview",
    "Regions",
    "Products & Categories",
    "Forecast",
    "Data"
])

with overview_tab:
    fig_monthly = px.line(
        monthly_sales,
        x="Year_Month",
        y="Sales",
        markers=True,
        title="Monthly Sales Trend",
        labels={"Year_Month": "Month", "Sales": "Total Sales (₹)"},
        template="plotly_white"
    )
    fig_monthly.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.subheader("📈 Revenue Mix")
    bar_col, pie_col = st.columns(2)

    with bar_col:
        fig_region = px.bar(
            region_sales,
            x="Region",
            y="Sales",
            title="Sales by Region",
            text_auto=".2s",
            labels={"Region": "Region", "Sales": "Total Sales (₹)"},
            template="plotly_white"
        )
        st.plotly_chart(fig_region, use_container_width=True)

    with pie_col:
        fig_region_pie = px.pie(
            region_sales,
            names="Region",
            values="Sales",
            title="Regional Sales Contribution",
            hole=0.4
        )
        st.plotly_chart(fig_region_pie, use_container_width=True)

with region_tab:
    col1, col2 = st.columns(2)
    with col1:
        fig_category = px.bar(
            category_sales,
            x="Category",
            y="Sales",
            title="Sales by Category",
            text_auto=".2s",
            labels={"Category": "Category", "Sales": "Total Sales (₹)"},
            template="plotly_white"
        )
        st.plotly_chart(fig_category, use_container_width=True)
    with col2:
        fig_category_pie = px.pie(
            category_sales,
            names="Category",
            values="Sales",
            title="Category Contribution",
            hole=0.4
        )
        st.plotly_chart(fig_category_pie, use_container_width=True)

with product_tab:
    fig_product = px.bar(
        product_sales,
        x="Product",
        y="Sales",
        title="Sales by Product",
        text_auto=".2s",
        labels={"Product": "Product", "Sales": "Total Sales (₹)"},
        template="plotly_white"
    )
    fig_product.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig_product, use_container_width=True)

    st.subheader("🏆 Top 5 Products by Sales")
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_top5 = px.bar(
            top_5_products.sort_values("Sales"),
            x="Sales",
            y="Product",
            orientation="h",
            title="Top 5 Performing Products",
            text_auto=".2s",
            labels={"Product": "Product", "Sales": "Total Sales (₹)"},
            template="plotly_white"
        )
        st.plotly_chart(fig_top5, use_container_width=True)
    with col2:
        st.markdown("### Top Products")
        for rank, (_, row) in enumerate(top_5_products.iterrows(), start=1):
            st.write(f"**{rank}. {row['Product']}**")
            st.write(f"Sales: ₹{row['Sales']:,.0f}")

with forecast_tab:
    st.subheader("📈 Monthly Sales Forecast")
    st.caption(
        "A simple linear trend estimate based on the filtered monthly sales. "
        "It is directional, not a guarantee, and does not model seasonality."
    )

    forecast_months = st.slider(
        "Forecast horizon (months)",
        min_value=1,
        max_value=12,
        value=3
    )

    historical_months = monthly_sales.copy()
    historical_months["Month"] = pd.PeriodIndex(
        historical_months["Year_Month"],
        freq="M"
    )

    if len(historical_months) < 3:
        st.info("Select a date range with at least three months of sales to view a forecast.")
    else:
        month_numbers = np.arange(len(historical_months), dtype=float)
        sales_values = historical_months["Sales"].to_numpy(dtype=float)
        slope, intercept = np.polyfit(month_numbers, sales_values, 1)
        future_numbers = np.arange(
            len(historical_months),
            len(historical_months) + forecast_months,
            dtype=float
        )
        predicted_sales = np.maximum(
            slope * future_numbers + intercept,
            0
        )
        future_periods = pd.period_range(
            start=historical_months["Month"].iloc[-1] + 1,
            periods=forecast_months,
            freq="M"
        )
        forecast_df = pd.DataFrame({
            "Month": future_periods.to_timestamp(),
            "Forecast Sales (₹)": predicted_sales
        })

        forecast_fig = px.line(
            historical_months.assign(
                Month=historical_months["Month"].dt.to_timestamp()
            ),
            x="Month",
            y="Sales",
            markers=True,
            title="Historical and Forecast Sales",
            labels={"Sales": "Sales (₹)"},
            template="plotly_white"
        )
        forecast_fig.update_traces(name="Historical sales", showlegend=True)
        forecast_fig.add_scatter(
            x=[
                historical_months["Month"].iloc[-1].to_timestamp(),
                *forecast_df["Month"]
            ],
            y=[sales_values[-1], *predicted_sales],
            mode="lines+markers",
            name="Forecast",
            line={"dash": "dash"}
        )
        forecast_fig.update_layout(xaxis_title="Month", yaxis_title="Sales (₹)")
        st.plotly_chart(forecast_fig, use_container_width=True)
        st.dataframe(
            forecast_df.assign(
                Month=forecast_df["Month"].dt.strftime("%b %Y"),
                **{"Forecast Sales (₹)": forecast_df["Forecast Sales (₹)"].map("₹{:,.0f}".format)}
            ),
            hide_index=True,
            use_container_width=True
        )
        st.download_button(
            label="Download Forecast CSV",
            data=forecast_df.to_csv(index=False).encode("utf-8"),
            file_name="sales_forecast.csv",
            mime="text/csv"
        )

with data_tab:
    st.dataframe(filtered_df, use_container_width=True)
    st.download_button(
        label="Download Filtered Sales Data",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="sales_analysis_data.csv",
        mime="text/csv"
    )

st.divider()

st.subheader("💡 Business Insights")

best_region = region_sales.iloc[0]["Region"] if not region_sales.empty else "N/A"
best_product = product_sales.iloc[0]["Product"] if not product_sales.empty else "N/A"
best_category = category_sales.iloc[0]["Category"] if not category_sales.empty else "N/A"
best_month = monthly_sales.loc[monthly_sales["Sales"].idxmax(), "Year_Month"] if not monthly_sales.empty else "N/A"

insight1, insight2 = st.columns(2)
with insight1:
    st.info(
        f"🌍 **Top Region:** {best_region}\n\n"
        "This region has the highest sales among the selected records."
    )
    st.info(
        f"📦 **Top Product:** {best_product}\n\n"
        "This product generates the highest sales revenue."
    )
with insight2:
    st.info(
        f"🏷️ **Top Category:** {best_category}\n\n"
        "This category contributes the highest sales revenue."
    )
    st.info(
        f"📅 **Best Sales Month:** {best_month}\n\n"
        "This month has the highest total sales in the selected period."
    )

st.markdown(
    "<center>Sales Data Analysis Project | Python • Pandas • Streamlit • Plotly</center>",
    unsafe_allow_html=True
)
