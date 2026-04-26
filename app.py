import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Stock AI Analysis", page_icon="📈")

# 2. Header Section
st.title("Stock Trend AI Analysis")
st.write("### (Results within 3 seconds)")

# 3. Search Input
symbol = st.text_input("Enter stock symbol (e.g., IRFC.NS or RELIANCE.NS)", value="IRFC.NS")
check_btn = st.button("Check Trend Now")

# 4. Logic & Analysis
if check_btn:
    with st.spinner('Fetching real-time data...'):
        try:
            # Fetch data (Last 6 months)
            data = yf.download(symbol, period="6mo", interval="1d")
            
            if not data.empty:
                # Fix for the "Series" error: Ensure we are looking at the 'Close' column only
                close_prices = data['Close'].squeeze()
                
                # Basic AI Logic: 20-day Simple Moving Average
                sma_20 = close_prices.rolling(window=20).mean()
                
                # Get latest values
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])
                
                st.metric(label=f"Current Price of {symbol}", value=f"₹{current_price:.2f}")
                
                # Trend Prediction Logic
                if current_price > latest_sma:
                    st.success("🚀 BULLISH TREND: Stock is currently strong.")
                else:
                    st.warning("📉 BEARISH TREND: Stock is currently weak.")
                
                # Visualizing the trend
                st.subheader("Price vs 20-Day Average")
                chart_data = pd.DataFrame({
                    'Price': close_prices,
                    'SMA20': sma_20
                })
                st.line_chart(chart_data)
                
            else:
                st.error("No data found. Please check the symbol (use .NS for NSE).")
        except Exception as e:
            st.error(f"Analysis Error: {e}")
