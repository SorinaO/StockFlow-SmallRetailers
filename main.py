import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# Sample stock data with categories
stock_data = {
    'Product': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Hat'],
    'Category': ['Clothing', 'Clothing', 'Clothing', 'Footwear', 'Accessories'],  # 🔴 Added "Category" column
    'Stock Level': [50, 200, 30, 100, 75],
    'Min Stock Level': [40, 100, 20, 50, 60],
    'Location': ['A1', 'B2', 'C3', 'D4', 'E5']
}

# Initialize session state for stock
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(stock_data)

# Function to display current stock with category filtering
def display_current_stock_overview():
    st.subheader("Current Stock Overview")

    # 🔴 Added dropdown to filter by category
    categories = ["All"] + list(st.session_state.df["Category"].unique())  
    selected_category = st.selectbox("Filter by Category", categories)  

    # 🔴 Apply filtering based on selected category
    filtered_df = st.session_state.df if selected_category == "All" else st.session_state.df[st.session_state.df["Category"] == selected_category]

    st.dataframe(filtered_df[['Product', 'Category', 'Stock Level', 'Min Stock Level', 'Location']])  # 🔴 Updated table to include "Category"

# Main function
def main():
    st.title("StockFlow - Small Retailers")
    display_current_stock_overview()  # 🔴 Updated to use the new category filter

if __name__ == "__main__":
    main()

