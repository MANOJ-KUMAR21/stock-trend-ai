import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Config & Header
st.set_page_config(page_title="Stock Trend AI", layout="centered")

# Matching the AD's text style
st.markdown("<h1 style='text-align: center; color: #0077b6;'>Stock AI Analysis</h1>", unsafe_all_html=True)
st.markdown("<p style='text-align: center; font-size: 20px;'><b>AI analysis trend (free)</b><br><span style='color: gray;'>Results within 3 seconds</span></p>", unsafe_all_html=True)

# 2. Search Logic (The .NS Fix)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    user_input = st.text_input("", placeholder="Enter stock name or symbol (e.g. IRFC)", key="search_bar")
    check_btn = st.button("Check now", use_container_width=True)

if check_btn and user_input:
    # Logic: If it's just a symbol like 'IRFC', add '.NS' for Indian Markets automatically
    symbol = user_input.upper().strip()
    if "." not in symbol:
        formatted_symbol = f"{symbol}.NS"
    else:
        formatted_symbol = symbol

    with st.spinner('Analyzing...'):
        try:
            data = yf.download(formatted_symbol, period="6mo", interval="1d")
            
            if not data.empty:
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                # The "Card" Look
                st.markdown(f"""
                <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="margin: 0; color: #333;">{symbol}</h2>
                    <h1 style="margin: 10px 0; color: #0077b6;">₹{current_price:.2f}</h1>
                </div>
                """, unsafe_all_html=True)

                # Trend Result
                if current_price > latest_sma:
                    st.success(f"🚀 BULLISH TREND: {symbol} is showing strong upward momentum.")
                else:
                    st.warning(f"📉 BEARISH TREND: {symbol} is currently trading below its average.")

                # Professional Chart
                chart_data = pd.DataFrame({'Price': close_prices, '20-Day Avg': sma_20})
                st.line_chart(chart_data)
            else:
                st.error("Could not find that stock. Try the exact symbol (e.g., RELIANCE).")
        except Exception as e:
            st.error("Please enter a valid stock symbol.")
