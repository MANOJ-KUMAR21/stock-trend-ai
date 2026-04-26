import streamlit as st
import yfinance as yf
import pandas as pd

# 1. UI Styling - Updated for compatibility
st.set_page_config(page_title="IRFC Stock AI", page_icon="📈")

# Cleaned up CSS block
custom_css = """
    <style>
    .stApp { background-color: #f9f4eb; }
    .stButton>button { width: 100%; background-color: #0077b6; color: white; border-radius: 5px; }
    </style>
    """
st.markdown(custom_css, unsafe_all_html=True)

# 2. Header Section
st.title("IRFC (543257)")
st.subheader("AI analysis trend (free)")
st.caption("Results within 3 seconds")

# 3. Search Input
# Using a unique key helps prevent "DuplicateWidgetID" errors
symbol = st.text_input("Enter stock symbol (e.g. IRFC.NS)", placeholder="IRFC.NS", key="stock_input")
check_btn = st.button("Check now")

# 4. Logic & Analysis
if check_btn and symbol:
    with st.spinner('Analyzing trend...'):
        try:
            # Fetch data
            data = yf.download(symbol, period="6mo", interval="1d")
            
            if not data.empty:
                # Basic AI Logic: Simple Moving Average (SMA)
                data['SMA20'] = data['Close'].rolling(window=20).mean()
                current_price = float(data['Close'].iloc[-1])
                sma_20 = float(data['SMA20'].iloc[-1])
                
                st.write(f"### Current Price: ₹{current_price:.2f}")
                
                # Trend Prediction
                if current_price > sma_20:
                    st.success("🚀 BULLISH TREND: Stock is trading above 20-day average.")
                else:
                    st.warning("📉 BEARISH TREND: Stock is below 20-day average.")
                
                # Show Chart
                st.line_chart(data[['Close', 'SMA20']])
            else:
                st.error("Stock symbol not found. For Indian stocks, add .NS (e.g., IRFC.NS)")
        except Exception as e:
            st.error(f"Error: {e}")
