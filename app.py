import streamlit as st
import yfinance as yf
import pandas as pd

# 1. UI Styling (Matching your image)
st.set_page_config(page_title="IRFC Stock AI", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #f9f4eb; }
    .stButton>button { width: 100%; background-color: #0077b6; color: white; border-radius: 5px; }
    .stock-box { border: 2px solid #d3d3d3; padding: 20px; border-radius: 10px; background: white; text-align: center; }
    </style>
    """, unsafe_all_html=True)

# 2. Header Section
st.title("IRFC (543257)")
st.subheader("AI analysis trend (free)")
st.caption("Results within 3 seconds")

# 3. Search Input
col1, col2 = st.columns([3, 1])
with col1:
    symbol = st.text_input("", placeholder="Enter stock symbol (e.g. IRFC.NS)")
with col2:
    check_btn = st.button("Check now")

# 4. Logic & Analysis
if check_btn and symbol:
    with st.spinner('Analyzing trend...'):
        try:
            # Fetch data (Last 6 months)
            data = yf.download(symbol, period="6mo", interval="1d")
            
            if not data.empty:
                # Basic AI Logic: Simple Moving Average (SMA)
                data['SMA20'] = data['Close'].rolling(window=20).mean()
                current_price = data['Close'].iloc[-1]
                sma_20 = data['SMA20'].iloc[-1]
                
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
