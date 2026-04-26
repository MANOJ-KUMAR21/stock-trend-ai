import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Stock AI Analysis", page_icon="📈")

# 2. Header Section
st.title("Stock Trend AI Analysis")
st.write("### (Results within 3 seconds)")

# 3. Search Input
# Using a clean layout without custom CSS to avoid the TypeError
symbol = st.text_input("Enter stock symbol (e.g., IRFC.NS or RELIANCE.NS)", value="IRFC.NS")
check_btn = st.button("Check Trend Now")

# 4. Logic & Analysis
if check_btn:
    with st.spinner('Fetching real-time data...'):
        try:
            # Fetch data (Last 6 months)
            data = yf.download(symbol, period="6mo", interval="1d")
            
            if not data.empty:
                # Basic AI Logic: 20-day Simple Moving Average
                data['SMA20'] = data['Close'].rolling(window=20).mean()
                
                # Get latest values and convert to standard Python floats
                current_price = float(data['Close'].iloc[-1])
                sma_20 = float(data['SMA20'].iloc[-1])
                
                st.metric(label=f"Current Price of {symbol}", value=f"₹{current_price:.2f}")
                
                # Trend Prediction Logic
                if current_price > sma_20:
                    st.success("🚀 BULLISH TREND: Stock is currently strong.")
                else:
                    st.warning("📉 BEARISH TREND: Stock is currently weak.")
                
                # Visualizing the trend
                st.subheader("Price vs 20-Day Average")
                st.line_chart(data[['Close', 'SMA20']])
                
            else:
                st.error("No data found. Please check the symbol (use .NS for NSE).")
        except Exception as e:
            st.error(f"Analysis Error: {e}")
