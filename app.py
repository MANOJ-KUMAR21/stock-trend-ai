import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_searchbox import st_searchbox

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Indian Stock AI", layout="centered")

# --- 2. CSS (Modified to add your photo background) ---
# Replace YOUR_IMAGE_DIRECT_LINK_HERE with your link, ensuring it stays inside the double quotes.
# Example: url("https://i.imgur.com/yourPhoto.jpg")
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("YOUR_IMAGE_DIRECT_LINK_HERE");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
    }}
    
    /* Center and Style Headers */
    .main-title {{
        font-size: 50px !important;
        font-weight: 800;
        text-align: center;
        color: #00d4ff;
        text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.6);
    }}
    
    .sub-title {{
        font-size: 20px;
        text-align: center;
        color: #ffd700; 
        font-weight: bold;
    }}

    /* Essential fixes for text visibility against a photo background */
    
    /* 1. Make all standard text white */
    .stApp p, .stApp label, .stApp div {{
        color: white !important;
    }}
    
    /* 2. Fix the searchbox dropdown text color (must be black/dark) */
    div[data-baseweb="select"] ul {{
        background-color: white !important;
    }}
    div[data-baseweb="select"] li {{
        color: black !important;
    }}
    
    /* 3. Style standard input boxes */
    div[data-baseweb="input"] input {{
        color: black !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }}

    /* 4. Style Metrics and boxes with a semi-transparent dark overlay */
    [data-testid="stMetric"], .stAlert {{
        background-color: rgba(0, 0, 0, 0.7) !important;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }}
    </style>
    """, unsafe_allow_html=True)
# --- 3. FUNCTIONS ---
@st.cache_data(ttl="1d")
def get_suggestions(search_term: str):
    if not search_term or len(search_term) < 2:
        return []
    try:
        # Standard search
        s = yf.Search(search_term, max_results=10)
        # Filter for Indian stocks
        return [(f"{q['shortname']} ({q['symbol']})", q['symbol']) 
                for q in s.quotes if q.get('symbol', '').endswith(('.NS', '.BO'))]
    except:
        return []

@st.cache_data(ttl="300s")
def get_data(symbol):
    return yf.download(symbol, period="6mo", interval="1d", progress=False)

# --- 4. UI ---
st.markdown('<h1 class="main-title">INDIAN STOCK AI</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ffd700;'>NSE & BSE Trend Predictor</p>", unsafe_allow_html=True)

selected_symbol = st_searchbox(
    get_suggestions,
    key="stock_search",
    placeholder="Type company name (e.g. Titan, Tata...)",
)

# Bring back the button for better control
check_btn = st.button("Check Trend Now", use_container_width=True)

# --- 5. LOGIC ---
if check_btn and selected_symbol:
    with st.spinner('Analyzing...'):
        data = get_data(selected_symbol)
        if not data.empty:
            close_prices = data['Close'].squeeze()
            sma_20 = close_prices.rolling(window=20).mean()
            current_price = float(close_prices.iloc[-1])
            latest_sma = float(sma_20.iloc[-1])

            st.divider()
            st.metric(label=f"Price: {selected_symbol}", value=f"₹{current_price:,.2f}")

            if current_price > latest_sma:
                st.success(f"🚀 BULLISH: {selected_symbol} is in a growth phase.")
            else:
                st.warning(f"📉 BEARISH: {selected_symbol} is showing weakness.")
            
            st.line_chart(pd.DataFrame({'Price': close_prices, 'Trend': sma_20}))
        else:
            st.error("No data found. Please try another stock.")
