import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_searchbox import st_searchbox

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Indian Stock AI", layout="centered")

# --- 2. CSS (Background, Premium Button & Text Visibility) ---
IMAGE_URL = "https://raw.githubusercontent.com/MANOJ-KUMAR21/stock-trend-ai/main/my_photo.jpg"

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url("{IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .main-title {{
        font-size: 45px !important;
        font-weight: 800;
        text-align: center;
        color: #00d4ff;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.6);
    }}
    .stApp p, .stApp label, .stApp div {{ color: white !important; }}
    
    /* Searchbox Fix: Ensure dropdown text is black and input text is visible */
    div[data-baseweb="select"] ul {{ background-color: white !important; }}
    div[data-baseweb="select"] li {{ color: black !important; }}
    input[data-testid="stWidgetLabel"] {{ color: white !important; }}
    
    /* PREMIUM BUTTON STYLE */
    div.stButton > button {{
        background: linear-gradient(45deg, #00d4ff, #0056b3) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
        height: 3em !important;
        transition: 0.3s !important;
        box-shadow: 0px 0px 15px rgba(0, 212, 255, 0.4) !important;
        text-transform: uppercase;
    }}
    div.stButton > button:hover {{
        box-shadow: 0px 0px 25px rgba(0, 212, 255, 0.8) !important;
        transform: scale(1.02) !important;
    }}

    [data-testid="stMetric"] {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. CACHED FUNCTIONS ---

@st.cache_data(ttl="1d")
def get_suggestions(search_term: str):
    if not search_term or len(search_term) < 2: return []
    try:
        s = yf.Search(search_term, max_results=10)
        return [(f"{q['shortname']} ({q['symbol']})", q['symbol']) 
                for q in s.quotes if q.get('symbol', '').endswith(('.NS', '.BO'))]
    except: return []

@st.cache_data(ttl="300s")
def get_data(symbol):
    # Flattening to avoid MultiIndex issues that cause empty charts
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

@st.cache_data(ttl="3600s")
def get_ai_recommendation(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        if hist.empty: return "NEUTRAL", "#808080"

        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        score = 0
        try:
            info = ticker.info
            current_price = hist['Close'].iloc[-1]
            target_price = info.get('targetMeanPrice')
            pe_ratio = info.get('trailingPE')
            if target_price and target_price > (current_price * 1.15): score += 2
            if pe_ratio and pe_ratio < 15: score += 1
        except: pass

        if rsi < 35: score += 2
        elif rsi > 65: score -= 2

        if score >= 3: return "STRONG BUY", "#00ff00"
        elif score >= 1: return "BUY", "#7cfc00"
        elif score <= -3: return "STRONG SELL", "#ff0000"
        elif score <= -1: return "SELL", "#ff4500"
        else: return "HOLD", "#ffd700"
    except: return "LIMIT REACHED", "#808080"

# --- 4. UI ---
st.markdown("<h1 class='main-title'>INDIAN STOCK'S TREND PREDICTION</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ffd700; font-weight: bold;'>AI Technical & Fundamental Analysis</p>", unsafe_allow_html=True)

selected_symbol = st_searchbox(get_suggestions, key="stock_search", placeholder="Enter stock (e.g. Reliance, TCS...)")
check_btn = st.button("Check Trend Now", use_container_width=True)

# --- 5. LOGIC ---
if check_btn and selected_symbol:
    with st.spinner('AI is analyzing market signals...'):
        data = get_data(selected_symbol)
        rec_text, rec_color = get_ai_recommendation(selected_symbol)
        
        if not data.empty:
            st.markdown(f"""
                <div style="background-color: rgba(0,0,0,0.6); padding: 25px; border-radius: 15px; border: 2px solid {rec_color}; text-align: center; margin-bottom: 20px;">
                    <h3 style="color: white; margin: 0; opacity: 0.8;">AI RECOMMENDATION</h3>
                    <h1 style="color: {rec_color}; margin: 0; font-size: 45px; text-shadow: 0 0 15px {rec_color};">{rec_text}</h1>
                </div>
            """, unsafe_allow_html=True)

            current_price = float(data['Close'].iloc[-1])
            st.metric(label=f"Current Price ({selected_symbol})", value=f"₹{current_price:,.2f}")
            
            st.write("### 6-Month Trend Analysis")
            # --- FIX FOR MISSING CHART LINES ---
            chart_df = pd.DataFrame({
                'Market Price': data['Close'],
                '20D Trend Line': data['Close'].rolling(window=20).mean()
            })
            st.line_chart(chart_df)
        else:
            st.error("No data found for this stock.")
