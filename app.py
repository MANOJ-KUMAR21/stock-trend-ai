import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_searchbox import st_searchbox

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Stock Trend AI", layout="centered")

# --- 2. CACHED FUNCTIONS (Defined outside any blocks) ---

@st.cache_data(ttl="1d")
def get_stock_suggestions(search_term: str):
    """Fetches suggestions and caches them for 1 day"""
    if not search_term or len(search_term) < 2:
        return []
    try:
        search = yf.Search(search_term, max_results=8)
        suggestions = [
            (f"{q['shortname']} ({q['symbol']})", q['symbol']) 
            for q in search.quotes 
            if 'shortname' in q
        ]
        return suggestions
    except Exception:
        return []

@st.cache_data(ttl="300s")
def get_stock_data(symbol):
    """Fetches stock price and caches for 5 minutes"""
    return yf.download(symbol, period="6mo", interval="1d", progress=False)

# --- 3. HEADER & UI SECTION ---
st.markdown("---")
col_a, col_b, col_c = st.columns([1, 4, 1])

with col_b:
    st.title("Stock AI Analysis")
    st.subheader("AI analysis trend (free)")
    
    # Use the CACHED search function here
    selected_symbol = st_searchbox(
        get_stock_suggestions,
        key="stock_search",
        placeholder="Type company name (e.g., Tata, Reliance...)",
        label="Search Stock Name or Symbol"
    )

# --- 4. RESULT LOGIC ---
if selected_symbol:
    with st.spinner(f'Analyzing {selected_symbol}...'):
        try:
            # Use the CACHED data function here
            data = get_stock_data(selected_symbol)
            
            if not data.empty:
                # Handle potential multi-index columns from yfinance
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
                chart_data = pd.DataFrame({
                    'Price': close_prices, 
                    'AI Trend (20D)': sma_20
                })
                st.line_chart(chart_data)
            else:
                st.error(f"No data found for {selected_symbol}")
                
        except Exception as e:
            st.error(f"Error fetching data: {e}")
