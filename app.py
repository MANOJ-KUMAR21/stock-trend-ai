import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="Stock Trend AI", layout="centered")

# --- 1. THE SEARCH FUNCTION ---
def search_stocks(search_term: str):
    """This function runs every time the user types a letter"""
    if not search_term or len(search_term) < 2:
        return []
    
    try:
        # Use yfinance search to get suggestions
        search = yf.Search(search_term, max_results=8)
        # Filter for NSE/BSE stocks and format for the dropdown
        # Returns a list of tuples: (Label to show user, Value to use in code)
        suggestions = [
            (f"{q['shortname']} ({q['symbol']})", q['symbol']) 
            for q in search.quotes 
            if 'shortname' in q
        ]
        return suggestions
    except Exception:
        return []

# --- 2. HEADER SECTION ---
st.markdown("---")
col_a, col_b, col_c = st.columns([1, 4, 1])

with col_b:
    st.title("Stock AI Analysis")
    st.subheader("AI analysis trend (free)")
    
    # THE SEARCH BAR (Replaces st.text_input)
    selected_symbol = st_searchbox(
        search_stocks,
        key="stock_search",
        placeholder="Type company name (e.g., Tata, Reliance...)",
        label="Search Stock Name or Symbol"
    )

# --- 3. RESULT LOGIC ---
# It triggers automatically when a symbol is selected from the dropdown
if selected_symbol:
    with st.spinner(f'Analyzing {selected_symbol}...'):
        try:
            data = yf.download(selected_symbol, period="6mo", interval="1d", progress=False)
            
            if not data.empty:
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                st.divider()
                st.metric(label=f"Real-time Price: {selected_symbol}", value=f"₹{current_price:,.2f}")

                if current_price > latest_sma:
                    st.success(f"🚀 BULLISH TREND: {selected_symbol} is in a growth phase.")
                else:
                    st.warning(f"📉 BEARISH TREND: {selected_symbol} is showing weakness.")

                st.write("### 6-Month Performance vs AI Trend Line")
                chart_data = pd.DataFrame({'Price': close_prices, 'AI Trend (20D)': sma_20})
                st.line_chart(chart_data)
        except Exception as e:
            st.error(f"Error fetching data: {e}")
