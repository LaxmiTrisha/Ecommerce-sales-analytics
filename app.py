
import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="E-commerce Sales Analytics",
    page_icon="🛒",
    layout="wide"
)

# --------------------------------------------------
# 2. FILE PATHS
# --------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent


def find_csv(filename):
    """Find a CSV in the src folder or project root."""
    possible_paths = [
        APP_DIR / filename,
        PROJECT_DIR / filename
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


# --------------------------------------------------
# 3. LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)


orders_path = find_csv("fact_master_orders.csv")
customers_path = find_csv("dim_customer_rfm.csv")


# --------------------------------------------------
# 4. DASHBOARD HEADER
# --------------------------------------------------
st.title("🛒 E-commerce Sales Analytics")

st.write(
    "Explore sales transactions and customer purchasing behavior."
)

st.divider()


# --------------------------------------------------
# 5. SALES AND ORDERS
# --------------------------------------------------
if orders_path is not None:

    orders = load_data(orders_path)

    st.header("📦 Sales and Orders")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", f"{len(orders):,}")

    if "order_id" in orders.columns:
        unique_orders = orders["order_id"].nunique()
        col2.metric("Unique Orders", f"{unique_orders:,}")
    else:
        col2.metric("Unique Orders", "N/A")

    col3.metric("Total Columns", f"{len(orders.columns):,}")

    # Sales overview
    if "price" in orders.columns:

        orders["price"] = pd.to_numeric(
            orders["price"], errors="coerce"
        )

        total_sales = orders["price"].sum()
        average_price = orders["price"].mean()

        st.subheader("💰 Sales Overview")

        col1, col2 = st.columns(2)

        col1.metric("Total Item Sales", f"{total_sales:,.2f}")
        col2.metric("Average Item Price", f"{average_price:,.2f}")

        st.caption(
            "Sales are calculated as the sum of item prices. "
            "Freight charges are excluded."
        )

        # Price distribution - fixed chart
        st.subheader("📊 Price Distribution")

        valid_prices = orders["price"].dropna()

        if not valid_prices.empty:

            price_bins = pd.cut(valid_prices, bins=10)

            price_chart = (
                price_bins.value_counts(sort=False)
                .rename_axis("Price Range")
                .reset_index(name="Number of Items")
            )

            # Convert intervals into ordinary text labels
            price_chart["Price Range"] = (
                price_chart["Price Range"].astype(str)
            )

            st.bar_chart(
                price_chart,
                x="Price Range",
                y="Number of Items",
                x_label="Price Range",
                y_label="Number of Items"
            )

        else:
            st.info("No valid price data available.")

    else:
        st.warning("The price column was not found in the order data.")

    # Order data preview
    st.subheader("📋 Order Data Preview")

    st.dataframe(
        orders.head(10),
        use_container_width=True,
        hide_index=True
    )

    # Interactive data explorer
    with st.expander("Explore Order Data"):

        selected_column = st.selectbox(
            "Choose a column to analyze",
            options=list(orders.columns)
        )

        value_counts = (
            orders[selected_column]
            .fillna("Missing")
            .astype(str)
            .value_counts()
            .head(10)
        )

        st.subheader("Top 10 Values")

        st.bar_chart(value_counts)

else:
    st.error(
        "Could not find fact_master_orders.csv. "
        "Place it in the src folder or project root."
    )


st.divider()


# --------------------------------------------------
# 6. CUSTOMER RFM ANALYSIS
# --------------------------------------------------
if customers_path is not None:

    customers = load_data(customers_path)

    st.header("👥 Customer RFM Analysis")

    col1, col2 = st.columns(2)

    col1.metric("Total Customer Records", f"{len(customers):,}")
    col2.metric("Customer Data Fields", f"{len(customers.columns):,}")

    # Customer segment distribution
    if "Customer_Segment" in customers.columns:

        st.subheader("🎯 Customer Segment Distribution")

        segment_counts = (
            customers["Customer_Segment"]
            .fillna("Unknown")
            .value_counts()
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.bar_chart(segment_counts)

        with col2:
            st.dataframe(
                segment_counts.rename_axis("Customer Segment")
                .reset_index(name="Customers"),
                use_container_width=True,
                hide_index=True
            )

    # RFM summary
    st.subheader("📈 RFM Summary")

    rfm_columns = [
        column for column in ["Recency", "Frequency", "Monetary"]
        if column in customers.columns
    ]

    if rfm_columns:
        st.dataframe(
            customers[rfm_columns].describe().round(2),
            use_container_width=True
        )

    # Customer preview
    st.subheader("📋 Customer Data Preview")

    st.dataframe(
        customers.head(10),
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning(
        "Could not find dim_customer_rfm.csv. "
        "Place it in the src folder or project root."
    )


# --------------------------------------------------
# 7. FOOTER
# --------------------------------------------------
st.divider()

st.caption(
    "E-commerce Sales Analytics | Python • SQL • Power BI"
)
