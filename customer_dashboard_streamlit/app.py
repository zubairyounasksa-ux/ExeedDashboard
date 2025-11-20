import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Customer Walk-in & Test Drive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH_DEFAULT = Path("data") / "Book Dashboard.xlsx"


@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    # Standardize column names
    df.columns = [str(c).strip() for c in df.columns]
    # Expected columns: Date, Walk-in Customer, Test Drive
    rename_map = {}
    for c in df.columns:
        lc = c.lower()
        if "date" in lc:
            rename_map[c] = "Date"
        elif "walk" in lc:
            rename_map[c] = "Walk-in Customer"
        elif "test" in lc and "drive" in lc:
            rename_map[c] = "Test Drive"
    df = df.rename(columns=rename_map)

    # Keep only required columns if present
    required_cols = ["Date", "Walk-in Customer", "Test Drive"]
    existing = [c for c in required_cols if c in df.columns]
    df = df[existing]

    # Clean up
    if "Date" in df.columns:
        df = df[~df["Date"].isna()]
        df["Date"] = pd.to_datetime(df["Date"]).dt.date

    if "Walk-in Customer" in df.columns:
        df["Walk-in Customer"] = pd.to_numeric(df["Walk-in Customer"], errors="coerce").fillna(0).astype(int)

    if "Test Drive" in df.columns:
        df["Test Drive"] = pd.to_numeric(df["Test Drive"], errors="coerce").fillna(0).astype(int)

    # Derived metrics
    if all(col in df.columns for col in ["Walk-in Customer", "Test Drive"]):
        df["Conversion Rate"] = df.apply(
            lambda row: (row["Test Drive"] / row["Walk-in Customer"]) * 100 if row["Walk-in Customer"] > 0 else 0,
            axis=1,
        )

    return df


def main():
    st.title("Customer Walk-in & Test Drive Dashboard")
    st.markdown(
        "Use this dashboard to monitor **daily showroom performance**, "
        "**test drive conversions**, and **overall customer funnel quality**."
    )

    # Sidebar: Data source
    st.sidebar.header("Data Source")
    uploaded_file = st.sidebar.file_uploader("Upload latest Excel file (.xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.sidebar.success("Using uploaded file")
    else:
        if DATA_PATH_DEFAULT.exists():
            df = load_data(str(DATA_PATH_DEFAULT))
            st.sidebar.info(f"Using default file: `{DATA_PATH_DEFAULT}`")
        else:
            st.error("No data file found. Please upload an Excel file from the sidebar.")
            return

    if df.empty:
        st.warning("No valid data found in the file.")
        return

    # Sidebar: Filters
    st.sidebar.header("Filters")
    if "Date" in df.columns:
        min_date = df["Date"].min()
        max_date = df["Date"].max()

        date_range = st.sidebar.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date

        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

    if df.empty:
        st.warning("No data in the selected date range.")
        return

    # KPI Section
    col1, col2, col3, col4 = st.columns(4)

    total_walkins = int(df["Walk-in Customer"].sum()) if "Walk-in Customer" in df.columns else 0
    total_testdrives = int(df["Test Drive"].sum()) if "Test Drive" in df.columns else 0
    total_days = df["Date"].nunique() if "Date" in df.columns else len(df)
    avg_walkins = total_walkins / total_days if total_days > 0 else 0
    overall_conversion = (total_testdrives / total_walkins * 100) if total_walkins > 0 else 0

    col1.metric("Total Walk-in Customers", f"{total_walkins}")
    col2.metric("Total Test Drives", f"{total_testdrives}")
    col3.metric("Overall Conversion Rate", f"{overall_conversion:.1f}%")
    col4.metric("Average Walk-ins per Day", f"{avg_walkins:.1f}")

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Daily Trend", "📊 Weekday Performance", "📉 Conversion Analysis", "📋 Raw Data"]
    )

    with tab1:
        st.subheader("Daily Walk-ins and Test Drives")
        if "Date" in df.columns:
            chart_df = df.set_index("Date")[["Walk-in Customer", "Test Drive"]]
            st.line_chart(chart_df)

    with tab2:
        st.subheader("Performance by Day of Week")
        if "Date" in df.columns:
            tmp = df.copy()
            tmp["Weekday"] = pd.to_datetime(tmp["Date"]).dt.day_name()
            agg = tmp.groupby("Weekday").agg(
                Walk_ins=("Walk-in Customer", "sum"),
                Test_Drives=("Test Drive", "sum"),
            )
            agg = agg.reindex(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            ).dropna(how="all")

            st.bar_chart(agg)

    with tab3:
        st.subheader("Daily Conversion Rate (%)")
        if "Conversion Rate" in df.columns and "Date" in df.columns:
            conv_df = df.set_index("Date")[["Conversion Rate"]]
            st.line_chart(conv_df)
            st.caption(
                "Conversion Rate = (Test Drives ÷ Walk-in Customers) × 100. "
                "Days with zero walk-ins are treated as 0% to avoid division errors."
            )

    with tab4:
        st.subheader("Raw Data")
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download filtered data as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_customer_data.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
