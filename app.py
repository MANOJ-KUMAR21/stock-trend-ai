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
    search_query = user_input.strip()
    
    with st.spinner('Searching for stock...'):
        try:
            # Step A: Try to find the ticker if they entered a name
            search = yf.Search(search_query, max_results=1)
            
            if search.quotes:
                # Get the best match ticker (e.g., "TATAMOTORS.NS")
                formatted_symbol = search.quotes[0]['symbol']
                display_name = search.quotes[0].get('shortname', formatted_symbol)
            else:
                # Step B: Fallback to your old logic if search finds nothing
                symbol = search_query.upper()
                formatted_symbol = f"{symbol}.NS" if "." not in symbol else symbol
                display_name = symbol.split(".")[0]

            # Step C: Download the data
            data = yf.download(formatted_symbol, period="6mo", interval="1d", progress=False)
            
            if not data.empty:
                # Handle MultiIndex and get last price
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                st.divider()
                # Use display_name so it looks clean (e.g., "Tata Motors Limited")
                st.metric(label=f"Real-time Price: {display_name}", value=f"₹{current_price:,.2f}")

                if current_price > latest_sma:
                    st.success(f"🚀 BULLISH TREND: {display_name} is in a growth phase.")
                else:
                    st.warning(f"📉 BEARISH TREND: {display_name} is showing weakness.")

                st.write("### 6-Month Performance vs AI Trend Line")
                chart_data = pd.DataFrame({
                    'Price': close_prices, 
                    'AI Trend (20D)': sma_20
                })
                st.line_chart(chart_data)
                
            else:
                st.error(f"Could not find data for '{search_query}'. Try the exact symbol (e.g. TATAMOTORS).")
        
        except Exception as e:
            st.error(f"Something went wrong: {e}")
