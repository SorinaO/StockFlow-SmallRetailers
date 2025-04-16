import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time



# 🔁 Add this counter to help reset the quantity input field
if "quantity_reset_counter" not in st.session_state:
    st.session_state.quantity_reset_counter = 0  # 🔁 Used to force quantity input to reset

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
    st.session_state.movement_log = []              # Keep track of stock movements


# Export stock data and movement logs as CSV
def export_data():
    st.subheader("Export Data")

    # Export stock data
    csv_stock = st.session_state.df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export Stock Data as CSV",
        data=csv_stock,
        file_name="stock_data.csv",
        mime="text/csv"
        )
    
    #Export movement log
    if st.session_state.movement_log:
        csv_log = pd.DataFrame(st.session_state.movement_log).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Movement Log as CSV",
            data=csv_log,
            file_name="movement_log.csv",
            mime="text/csv"
        )


# 📊 Show current stock with optional category filter
def display_current_stock_overview(key_suffix=""):
    st.subheader("Current Stock Overview")

    categories = ["All"] + list(st.session_state.df["Category"].unique())
    selected_category = st.selectbox("Filter by Category", categories, key=f"category_filter_overview_{key_suffix}")

    # 🔍 Filter table by category
    filtered_df = st.session_state.df if selected_category == "All" else st.session_state.df[st.session_state.df["Category"] == selected_category]

    # ⚠️ Alert for low stock
    for index, row in filtered_df.iterrows():
        if row["Stock Level"] < row["Min Stock Level"]:
            st.warning(f"{row['Product']} is below the minimum stock level!")

    # 📋 Show the filtered stock table
    st.dataframe(filtered_df[['Product', 'Category', 'Stock Level', 'Min Stock Level', 'Location']])


# 🔧 Log and update stock based on type of movement
def log_stock_movement():
    st.subheader("Log Stock Movement")

    product = st.selectbox("Select Product", st.session_state.df["Product"].tolist(), key = "product_select")
    movement_type = st.selectbox("Movement Type", ["New Stock Arrival", "Customer Return", "Customer Order", "Damaged", "Discrepancy", "Supplier Return"], key="movement_type")

    
    # Dynamically reset the quantity input field using a session state counter
    quantity_key = f"quantity_input_{st.session_state.quantity_reset_counter}"
    quantity = st.number_input(
        "Quantity", 
        min_value=1, 
        max_value=500, 
        value=1, 
        key=quantity_key  # Dynamic key ensures reset
    )
    
    if st.button("Submit Movement"):
        # Determine sign of the quantity change
        if movement_type in["New Stock Arrival", "Customer Return"]:
            delta = quantity
        else:
            delta = -quantity

        st.session_state.df.loc[st.session_state.df["Product"] == product, "Stock Level"] += delta

        # Log the movement
        st.session_state.movement_log.append({"Product": product,
                                               "Movement Type": movement_type,
                                                 "Quantity": quantity,
                                                   "Time": time.strftime("%Y-%m-%d %H:%M:%S")
                                                   })
        
        st.success(f"Logged {movement_type} of {quantity} for {product}.")
        time.sleep(2)  # Optional: Add a small delay for user feedback
        st.session_state.quantity_reset_counter += 1
        st.rerun()  # Force the app to rerun to refresh the UI


# 📘 View movement log
def view_movement_log():
    if st.session_state.movement_log:
        st.subheader("Movement Log")
        log_df = pd.DataFrame(st.session_state.movement_log)
        st.dataframe(log_df)


# 🚀 MAIN APP
def main():
    st.title("StockFlow - Small Retailers")
    display_current_stock_overview(key_suffix="main") # 👁️ View the current stock with filters
    log_stock_movement()                              # ➕➖ Log inbound/outbound movements
    view_movement_log()                               # 📘 Log of all recent stock movements
    export_data()                                     # Call the export_data function

if __name__ == "__main__":
    main()
