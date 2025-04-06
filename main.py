import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# 📦 Sample stock data with categories
stock_data = {
    'Product': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Hat'],
    'Category': ['Clothing', 'Clothing', 'Clothing', 'Footwear', 'Accessories'],  # 🧢 Added "Category" column
    'Stock Level': [50, 200, 30, 100, 75],
    'Min Stock Level': [40, 100, 20, 50, 60],
    'Location': ['A1', 'B2', 'C3', 'D4', 'E5']
}

# 🧠 SESSION STATE INIT: Only runs once when the app starts
if "adjustment_value" not in st.session_state:
    st.session_state.adjustment_value = 0  # For remembering the input value between runs

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(stock_data)  # Load the data
    st.session_state.last_selected_product = None   # Track the last selected product


# 📊 Show current stock with optional category filter
def display_current_stock_overview():
    st.subheader("Current Stock Overview")

    categories = ["All"] + list(st.session_state.df["Category"].unique())
    selected_category = st.selectbox("Filter by Category", categories, key="category_filter_overview")

    # 🔍 Filter table by category
    filtered_df = st.session_state.df if selected_category == "All" else st.session_state.df[st.session_state.df["Category"] == selected_category]

    # ⚠️ Alert for low stock
    for index, row in filtered_df.iterrows():
        if row["Stock Level"] < row["Min Stock Level"]:
            st.warning(f"{row['Product']} is below the minimum stock level!")

    # 📋 Show the filtered stock table
    st.dataframe(filtered_df[['Product', 'Category', 'Stock Level', 'Min Stock Level', 'Location']])


# 🔧 Adjust the stock levels of products
def adjust_stock_level():
    st.subheader("Adjust Stock Levels")

    # 🧾 Dropdown to choose which product to update
    selected_product = st.selectbox(
        "Select Product to Adjust",
        st.session_state.df["Product"].tolist(),
        index=0,
        key="product_selectbox_adjust"
    )

    # 🧠 Reset input value when switching products
    if selected_product != st.session_state.last_selected_product:
        st.session_state.last_selected_product = selected_product
        adjustment_value = 0
    else:
        adjustment_value = st.session_state.adjustment_value

    # 🔢 Let user input adjustment amount
    adjustment = st.number_input(
        "Enter Adjustment Amount",
        min_value=-100,
        max_value=100,
        value=adjustment_value,
        key="adjustment_value"
    )

    # ✅ Apply the adjustment
    if st.button("Apply Adjustment"):
        st.session_state.df.loc[
            st.session_state.df["Product"] == selected_product, "Stock Level"
        ] += adjustment

        st.success(
            f"Stock Level for {selected_product} adjusted by {adjustment}. "
            f"New stock level: {st.session_state.df.loc[st.session_state.df['Product'] == selected_product, 'Stock Level'].values[0]}"
        )

        # 🔄 Reset the product tracker
        st.session_state.last_selected_product = None
        

# 🚀 MAIN APP
def main():
    st.title("StockFlow - Small Retailers")
    display_current_stock_overview()  # 👁️ View the current stock with filters
    adjust_stock_level()              # 🛠️ Adjust stock amounts here

if __name__ == "__main__":
    main()
