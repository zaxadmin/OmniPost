import streamlit as st
from supabase import create_client

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

st.markdown("""
    <style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; }
    
    /* Footer & Éléments Légaux */
    .footer-text { text-align: center; font-size: 11px; color: gray; margin-top: 50px; padding-bottom: 20px; border-top: 1px solid #eee; padding-top: 20px; }
    .footer-links a { color: #F3812B; text-decoration: none; margin: 0 10px; font-weight: bold; }
    
    /* Système de Tri & Bannettes */
    .legend-box { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; display: flex; justify-content: space-around; flex-wrap: wrap; }
    .dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .bannette-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; border-left: 5px solid #ddd; }
    .border-top { border-left-color: #2e7d32 !important; }
    .border-chance { border-left-color: #F3812B !important; }
