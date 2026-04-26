import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Stock Trend AI", layout="centered")

# 2. Centered Header Section (Native Streamlit)
# This mimics the "IRFC (543257)" header from your ad
st.markdown("---") # Visual line to separate from the browser bar
col_a, col_b, col_c = st.columns([1, 4, 1])

with col_b:
    st.title("Stock AI Analysis")
    st.subheader("AI analysis trend (free)")
    st.write("⏱️ Results within 3 seconds")

    # 3. The Search Bar (Centered)
    user_input = st.text_input("Enter stock name or symbol", value="IRFC", help="Try: RELIANCE, TCS, or TITAN")
    check_btn = st.button("Check Trend Now", use_container_width=True)

# 4. Result Logic
if check_btn and user_input:
    symbol = user_input.upper().strip()
    # Auto-add .NS for Indian stocks if no suffix is provided
    formatted_symbol = f"{symbol}.NS" if "." not in symbol else symbol

    with st.spinner('Calculating...'):
        try:
            data = yf.download(formatted_symbol, period="6mo", interval="1d")
            
            if not data.empty:
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                # The "White Card" Look (Native Metric)
                st.divider()
                st.metric(label=f"Real-time Price: {symbol}", value=f"₹{current_price:,.2f}")

                # Trend Result Message
                if current_price > latest_sma:
                    st.success(f"🚀 BULLISH TREND: {symbol} is currently in a strong growth phase.")
                else:
                    st.warning(f"📉 BEARISH TREND: {symbol} is currently showing weakness.")

                # Professional Chart
                st.write("### 6-Month Performance vs AI Trend Line")
                chart_data = pd.DataFrame({
                    'Price': close_prices, 
                    'AI Trend (20D)': sma_20
                })
                st.line_chart(chart_data)
                
            else:
                st.error(f"Symbol '{symbol}' not found. Try adding .NS manually.")
        except Exception:
            st.error("Connection error. Please refresh.")
