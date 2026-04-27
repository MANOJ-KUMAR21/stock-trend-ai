import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_searchbox import st_searchbox

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Stock Trend AI", layout="centered")

# --- 2. CUSTOM CSS (The "Nice Background" Logic) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Center the titles and make them pop */
    h1, h3 {
        text-align: center;
        color: #1e3a8a;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Style the Searchbox container */
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    
    /* Make metrics cards look premium */
    [data-testid="stMetricValue"] {
        font-size: 30px;
        color: #1e3a8a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CACHED FUNCTIONS ---

@st.cache_data(ttl="1d")
def get_stock_suggestions(search_term: str):
    if not search_term or len(search_term) < 2:
        return []
    try:
        search = yf.Search(search_term, max_results=8)
        return [(f"{q['shortname']} ({q['symbol']})", q['symbol']) for q in search.quotes if 'shortname' in q]
    except Exception:
        return []

@st.cache_data(ttl="300s")
def get_stock_data(symbol):
    return yf.download(symbol, period="6mo", interval="1d", progress=False)

# --- 4. UI SECTION ---
col_a, col_b, col_c = st.columns([1, 4, 1])

with col_b:
    st.title("📈 Stock AI Analysis")
    st.markdown("<p style='text-align: center; color: gray;'>AI-powered trend analysis for Indian Markets</p>", unsafe_allow_html=True)
    
    selected_symbol = st_searchbox(
        get_stock_suggestions,
        key="stock_search",
        placeholder="Type company (e.g. Tata Motors, Reliance...)",
        label="Enter Stock Name"
    )

# --- 5. RESULT LOGIC ---
if selected_symbol:
    with st.spinner(f'Analyzing {selected_symbol}...'):
        try:
            data = get_stock_data(selected_symbol)
            
            if not data.empty:
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                # Layout for results
                st.markdown("---")
                st.metric(label=f"Price: {selected_symbol}", value=f"₹{current_price:,.2f}")

                if current_price > latest_sma:
                    st.success(f"🚀 **BULLISH TREND**: {selected_symbol} is in a strong growth phase.")
                else:
                    st.warning(f"📉 **BEARISH TREND**: {selected_symbol} is showing weakness.")

                st.write("### AI Performance Chart")
                chart_data = pd.DataFrame({'Price': close_prices, 'AI Trend (20D)': sma_20})
                st.line_chart(chart_data)
            else:
                st.error("No data found.")
        except Exception as e:
            st.error(f"Error: {e}")
