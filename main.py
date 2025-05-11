import streamlit as st
import pandas as pd
import time
import plotly.express as px # for data visualisation
from datetime import datetime

# Function to load the data from CSV
def load_data_from_csv(filename = "stock_data.csv"):
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Product", "Category", "Stock Level", "Min Stock Level", "Location" ])
    

# Function to save data to CSV
def save_data_to_csv(df, filename="stock_data.csv"):
    df.to_csv(filename, index=False)

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
    # Load stock data from CSV instead of hardcoded data
    st.session_state.df = load_data_from_csv() 
    if st.session_state.df.empty:                   # If no CSV exists, initialize with sample data
        st.session_state.df = pd.DataFrame(stock_data) 
        save_data_to_csv(st.session_state.df)       # Save the sample data to CSV
    st.session_state.last_selected_product = None   # Track the last selected product
    st.session_state.movement_log = []              # Keep track of stock movements


def visualise_stock_trends():
    st.subheader("Stock Levels and Trends")

    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)

    # Bar chart: Stock levels by product and category
    fig = px.bar(
        st.session_state.df,
        x="Product",
        y="Stock Level",
        color="Category",
        title="Stock Levels by Product and Category",
        labels={"Stock Level": "Current Stock Level"}
    )

    # Display bar chart in the left column
    with col1:
        st.plotly_chart(fig, use_container_width=True)

    # Line chart: Stock levels over time (if movement logs exist)
    if st.session_state.movement_log:
        log_df = pd.DataFrame(st.session_state.movement_log)
        log_df["Time"] = pd.to_datetime(log_df["Time"])  # Convert Time column to datetime
        log_df = log_df.sort_values(by="Time")  # Sort by time for proper plotting

        fig2 = px.line(
            log_df,
            x="Time",
            y="Quantity",
            color="Product",
            title="Historical Stock Movements Over Time",
            labels={"Quantity": "Movement Quantity"},
            color_discrete_sequence=px.colors.qualitative.Plotly,
            custom_data=["Movement Type"]   # Pass movement type to customdat
        )

# Add hover tooltips
        fig2.update_traces(hovertemplate="Time: %{x|%y-%m-%d %H:%M:%S}<br>Product: %{legend}<br>Movement Type:%{customdata[0]}<br>Quantity: %{y}")

        # Display line chart in the right column
        with col2:
            st.plotly_chart(fig2, use_container_width=True)

        # Optional: Add a summary table with the date included
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Get the current date and time

        # Optional: Add a summary table
        summary_df = pd.DataFrame({
            'Metric': [
                'Total Sales',
                  'Total Restocks (Stock Arrivals)',
                    'Total Returns',
                    "Total Discrepancies"
            ],
            'Value': [
                log_df[log_df['Movement Type'] == 'Customer Order']['Quantity'].sum(),
                log_df[log_df['Movement Type'] == 'New Stock Arrival']['Quantity'].sum(),
                log_df[log_df['Movement Type'] == 'Customer Return']['Quantity'].sum(),
                log_df[log_df['Movement Type'] == 'Discrepancy']['Quantity'].sum()
            ],
            "Last Updated": [current_date] * 4 # Update to include four rows
        })
        st.table(summary_df)

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

    # Export movement log
    if st.session_state.movement_log:
        csv_log = pd.DataFrame(st.session_state.movement_log).to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export Movement Log as CSV",
            data=csv_log,
            file_name="movement_log.csv",
            mime="text/csv"
        )

# Upload Data Feature       
def upload_data():
    st.subheader("Upload Stock Data")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            # Read the uploaded CSV file
            new_data = pd.read_csv(uploaded_file)

            # Validate the data
            required_columns = ["Product", "Category", "Stock Level", "Min Stock Level", "Location"]
            if not all(col in new_data.columns for col in required_columns):
                st.error("Uploaded file is missing required columns.")
                return
            
            # Update the stock data in session state
            st.session_state.df = new_data

            # Save the updated data to a persistent CSV file
            save_data_to_csv(new_data)

            st.success("Data successfully uploaded and saved!")

            time.sleep(2)
            st.rerun() # Force the app to rerun to refresh the UI

        except Exception as e:
            st.error(f"Error processing the file: {e}")


# 📊 Show current stock with optional category filter
def display_current_stock_overview(key_suffix=""):
    st.subheader("Current Stock Overview")

    categories = ["All"] + list(st.session_state.df["Category"].unique())
    selected_category = st.selectbox("Filter by Category", categories, key=f"category_filter_overview_{key_suffix}")

    # 🔍 Filter table by category
    filtered_df = st.session_state.df if selected_category == "All" else st.session_state.df[
        st.session_state.df["Category"] == selected_category]

    # ⚠️ Alert for low stock
    for index, row in filtered_df.iterrows():
        if row["Stock Level"] < row["Min Stock Level"]:
            st.warning(f"{row['Product']} is below the minimum stock level!")

    # 📋 Show the filtered stock table
    st.dataframe(filtered_df[['Product', 'Category', 'Stock Level', 'Min Stock Level', 'Location']])


# 🔧 Log and update stock based on type of movement
def log_stock_movement():
    st.subheader("Log Stock Movement")

    product = st.selectbox("Select Product", st.session_state.df["Product"].tolist(), key="product_select")
    movement_type = st.selectbox(
        "Movement Type",
        ["New Stock Arrival", "Customer Return", "Customer Order", "Damaged", "Discrepancy", "Supplier Return"],
        key="movement_type"
    )

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
        if movement_type in ["New Stock Arrival", "Customer Return"]:
            delta = quantity
        else:
            delta = -quantity

        st.session_state.df.loc[st.session_state.df["Product"] == product, "Stock Level"] += delta

        # Log the movement
        st.session_state.movement_log.append({
            "Product": product,
            "Movement Type": movement_type,
            "Quantity": quantity,
            "Time": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Save updated stock data to CSV
        save_data_to_csv(st.session_state.df)

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
        display_current_stock_overview(key_suffix="main")  # 👁️ View the current stock with filters
        log_stock_movement()                              # ➕➖ Log inbound/outbound movements
        view_movement_log()                               # 📘 Log of all recent stock movements
        export_data()                                     # Call the export_data function
        visualise_stock_trends()                          # Visualise Stock Trends
        upload_data()                                     # Add the upload data feature

if __name__ == "__main__":
    main()
