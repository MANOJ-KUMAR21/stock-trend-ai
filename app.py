import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_searchbox import st_searchbox

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Stock Trend AI - India", layout="centered")

# --- 2. ADVANCED CSS (Dark Fintech Theme) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                    url("https://images.unsplash.com/photo-1611974714851-eb60516122d6?q=80&w=2070");
        background-size: cover;
        color: white;
    }
    .main-title {
        font-size: 45px !important;
        font-weight: 800;
        text-align: center;
        color: #00d4ff;
        text-shadow: 0px 0px 10px rgba(0, 212, 255, 0.5);
    }
    .sub-title {
        font-size: 18px;
        text-align: center;
        color: #ffd700;
        margin-top: -10px;
        font-weight: bold;
    }
    /* Style the Searchbox to be visible in dark mode */
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid #00d4ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CACHED FUNCTIONS (Filtered for India) ---

@st.cache_data(ttl="1d")
def get_stock_suggestions(search_term: str):
    if not search_term or len(search_term) < 2:
        return []
    try:
        # We fetch more results to ensure we find enough Indian matches
        search = yf.Search(search_term, max_results=20)
        
        suggestions = []
        for q in search.quotes:
            symbol = q.get('symbol', '')
            # FILTER: Only keep symbols ending in .NS or .BO
            if symbol.endswith('.NS') or symbol.endswith('.BO'):
                name = q.get('shortname', symbol)
                suggestions.append((f"{name} ({symbol})", symbol))
        
        return suggestions
    except Exception:
        return []

@st.cache_data(ttl="300s")
def get_stock_data(symbol):
    return yf.download(symbol, period="6mo", interval="1d", progress=False)

# --- 4. UI SECTION ---
st.markdown('<h1 class="main-title">INDIAN STOCK AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">NSE & BSE Trend Predictor</p>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns([1, 6, 1])
with col_b:
    selected_symbol = st_searchbox(
        get_stock_suggestions,
        key="stock_search",
        placeholder="Search (e.g. SBI, Tata, Reliance...)",
    )

# --- 5. RESULT LOGIC ---
if selected_symbol:
    with st.spinner('Fetching Indian Market Data...'):
        try:
            data = get_stock_data(selected_symbol)
            
            if not data.empty:
                # Cleaning data for multi-index issues
                close_prices = data['Close'].squeeze()
                sma_20 = close_prices.rolling(window=20).mean()
                current_price = float(close_prices.iloc[-1])
                latest_sma = float(sma_20.iloc[-1])

                st.divider()
                st.metric(label=f"Current Value ({selected_symbol})", value=f"₹{current_price:,.2f}")

                if current_price > latest_sma:
                    st.success(f"🚀 BULLISH: {selected_symbol} is trading above the 20-day trend line.")
                else:
                    st.warning(f"📉 BEARISH: {selected_symbol} is currently showing downward pressure.")

                # Professional Dark Chart
                chart_df = pd.DataFrame({
                    'Market Price': close_prices, 
                    'AI Trend Line': sma_20
                })
                st.line_chart(chart_df)
                
            else:
                st.error("Market data currently unavailable for this symbol.")
        except Exception as e:
            st.error(f"Error: {e}")
