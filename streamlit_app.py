import streamlit as st
import pandas as pd

# Page config
st.set_page_config(
    page_title="Income Statement App",
    layout="wide"
)

st.title("Consolidated Income Statement App")

# Upload section
uploaded_file = st.file_uploader("Upload Income Statement File (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Validate file
    required_cols = {"Product", "Metric", "Value"}
    if not required_cols.issubset(df.columns):
        st.error(f"Uploaded file must contain columns: {required_cols}")
        st.stop()

    # Build product dictionaries
    all_products = {}
    for product in df["Product"].unique():
        product_data = (
            df[df["Product"] == product]
            .set_index("Metric")["Value"]
            .to_dict()
        )
        all_products[product] = product_data

    # Sidebar: instructions & selection
    with st.sidebar:
        st.title("Instructions")
        st.write("1. Upload your file above.")
        st.write("2. Select one or more products.")
        st.write("3. View metrics and charts.")
        st.write("---")

        products_available = list(all_products.keys())
        selected_products = st.multiselect(
            "Select products:",
            products_available,
            default=products_available
        )

    if not selected_products:
        st.warning("Please select at least one product.")
        st.stop()

    # Compute totals
    totals = {}
    for prod in selected_products:
        for key, val in all_products[prod].items():
            totals[key] = totals.get(key, 0) + val

    # Perform calculations
    tax_rate = 0.27

    Interest_received = totals["Interest received"]
    Cost_of_Funds_incl_liquids = totals["Cost of Funds incl liquids"]
    gross_lending_margin = totals["Interest received"] + totals["Cost of Funds incl liquids"]
    Return_on_Capital_Invested = totals["Return on Capital Invested"]
    Credit_Premium = totals["Credit Premium"]
    Lending_margin_after_Credit_Premium = (
        gross_lending_margin +
        totals["Return on Capital Invested"] +
        totals["Credit Premium"]
    )
    Other_credit_based_fee_income = totals["Other credit based fee income"]
    Overheads_related_to_lending_business = totals["Overheads related to lending business"]
    Additional_Tier_1_Cost_of_Capital = totals["Additional Tier 1 Cost of Capital"]
    Tier_2_Cost_of_Capital = totals["Tier 2 Cost of Capital"]
    LIBT = (
        Lending_margin_after_Credit_Premium +
        totals["Other credit based fee income"] +
        totals["Overheads related to lending business"] +
        totals["Additional Tier 1 Cost of Capital"] +
        totals["Tier 2 Cost of Capital"]
    )
    taxation = LIBT * tax_rate
    LIACC = LIBT - taxation + totals["Core Equity Tier 1 Cost Of Capital"]

    ROE = (
        ((LIBT - taxation) / totals["Core equity capital holding"]) * 100
        if totals["Core equity capital holding"] != 0 else 0
    )

    # Results section
    st.write("---")
    st.markdown(f"### Results for: {', '.join(selected_products)}")

    # Metrics dashboard
    col1, col2, col3 = st.columns(3)
    col1.metric("Gross Lending Margin", f"{gross_lending_margin:,.0f}")
    col2.metric("LIBT", f"{LIBT:,.0f}")
    col3.metric("ROE (%)", f"{ROE:.2f}%")

    # Detailed table
    results_df = pd.DataFrame({
        "Metric": [
            "Interest received",
            "Cost of Funds incl liquids",
            "Gross Lending Margin",
            "Return on Capital Invested",
            "Credit Premium",
            "Lending Margin after Credit Premium",
            "Other credit based fee income",
            "Overheads related to lending business",
            "Additional Tier 1 Cost of Capital",
            "Tier 2 Cost of Capital",
            "LIBT",
            "Taxation",
            "LIACC",
            "ROE (%)"
        ],
        "Value": [
            Interest_received,
            Cost_of_Funds_incl_liquids,
            gross_lending_margin,
            Return_on_Capital_Invested,
            Credit_Premium,
            Lending_margin_after_Credit_Premium,
            Other_credit_based_fee_income,
            Overheads_related_to_lending_business,
            Additional_Tier_1_Cost_of_Capital,
            Tier_2_Cost_of_Capital,
            LIBT,
            taxation,
            LIACC,
            ROE
        ]
    })

    # Highlighting function
    def highlight_metrics(row):
        if row["Metric"] == "ROE (%)":
            return ['background-color: lightgreen'] * 2
        elif row["Metric"] in [
            "Gross Lending Margin",
            "Lending Margin after Credit Premium",
            "LIBT",
            "LIACC"
        ]:
            return ['background-color: #FFD580'] * 2  # light orange
        else:
            return [''] * 2

    st.write("---")
    st.subheader("Detailed Results Table")

    st.dataframe(
        results_df.style
        .format({"Value": "{:,.2f}"})
        .apply(highlight_metrics, axis=1)
    )

    # Chart
    chart_df = pd.DataFrame({
        "Metric": ["Gross Lending Margin", "LIBT", "LIACC"],
        "Value": [gross_lending_margin, LIBT, LIACC]
    })

    st.write("---")
    st.subheader("Key Metrics Chart")
    st.bar_chart(chart_df.set_index("Metric"))

else:
    st.info("Please upload a file to begin.")
