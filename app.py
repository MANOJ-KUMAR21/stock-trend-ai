import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Stock Trend AI", layout="centered")

# 2. Header Section
st.markdown("---") 
col_a, col_b, col_c = st.columns([1, 4, 1])

with col_b:
    st.title("Stock AI Analysis")
    st.subheader("AI analysis trend (free)")
    st.write("⏱️ Results within 3 seconds")

    user_input = st.text_input("Enter stock name or symbol", value="IRFC", help="Try: RELIANCE, TCS, or TITAN")
    check_btn = st.button("Check Trend Now", use_container_width=True)

# 4. Result Logic
if check_btn and user_input:
    # CLEANING LOGIC
    raw_input = user_input.upper().strip()
    
    # 1. Handle common name-to-symbol mapping (Expansion point)
    name_map = {
        "SHIPPING CORPORATION": "SCI",
        "TATA MOTORS": "TATAMOTORS",
        "RELIANCE INDUSTRIES": "RELIANCE"
    }
    
    # If user typed a name from our map, use the symbol instead
    symbol_only = name_map.get(raw_input, raw_input)
    
    # 2. Format for yfinance (Backend)
    # Ensure it has .NS for Indian stocks, but keep a 'display_name' clean
    if "." not in symbol_only:
        formatted_symbol = f"{symbol_only}.NS"
        display_name = symbol_only
    else:
        formatted_symbol = symbol_only
        display_name = symbol_only.split(".")[0]

    with st.spinner('Calculating...'):
        try:
            # We use 'formatted_symbol' for the fetch
            data = yf.download(formatted_symbol, period="6mo", interval="1d", progress=False)
            
            if not data.empty:
                # Use squeeze() to handle the MultiIndex columns yfinance sometimes returns
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                st.divider()
                # We use 'display_name' here so the user doesn't see .NS
                st.metric(label=f"Real-time Price: {display_name}", value=f"₹{current_price:,.2f}")

                if current_price > latest_sma:
                    st.success(f"🚀 BULLISH TREND: {display_name} is currently in a strong growth phase.")
                else:
                    st.warning(f"📉 BEARISH TREND: {display_name} is currently showing weakness.")

                st.write("### 6-Month Performance vs AI Trend Line")
                chart_data = pd.DataFrame({
                    'Price': close_prices, 
                    'AI Trend (20D)': sma_20
                })
                st.line_chart(chart_data)
                
            else:
                st.error(f"Could not find data for '{raw_input}'. If it's a name, try the exact Ticker Symbol.")
        except Exception as e:
            st.error(f"Error: {e}. Please try a different symbol.")
