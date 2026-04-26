import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Stock Trend AI", layout="centered")

# 2. Native Header (No HTML to avoid TypeErrors)
st.title("Stock AI Analysis")
st.write("### AI analysis trend (free)")
st.caption("Results within 3 seconds")

# 3. Search Logic
# This handles the .NS requirement automatically
user_input = st.text_input("Enter stock name or symbol", value="IRFC", help="Example: IRFC, RELIANCE, TCS")
check_btn = st.button("Check Trend Now", use_container_width=True)

if check_btn and user_input:
    # Auto-format symbol
    symbol = user_input.upper().strip()
    formatted_symbol = f"{symbol}.NS" if "." not in symbol else symbol

    with st.spinner('Analyzing...'):
        try:
            # Download data
            data = yf.download(formatted_symbol, period="6mo", interval="1d")
            
            if not data.empty:
                # Process data
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                # Display Results using native st.metric (looks very clean)
                st.divider()
                st.metric(label=f"Current Price: {symbol}", value=f"₹{current_price:.2f}")

                # Trend Result
                if current_price > latest_sma:
                    st.success(f"🚀 BULLISH TREND: {symbol} is trading above its 20-day average.")
                else:
                    st.warning(f"📉 BEARISH TREND: {symbol} is trading below its 20-day average.")

                # Professional Chart
                st.subheader("6-Month Price Trend")
                chart_data = pd.DataFrame({
                    'Price': close_prices, 
                    '20-Day Avg': sma_20
                })
                st.line_chart(chart_data)
                
            else:
                st.error(f"Could not find '{symbol}'. Please try the official symbol.")
        except Exception as e:
            st.error("Connection error. Please try again in a few seconds.")
