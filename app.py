import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

st.markdown("""
    <style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; }
    
    /* Guide des Couleurs & Légende */
    .legend-box { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; display: flex; justify-content: space-around; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; font-size: 13px; margin: 5px; }
    .dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    
    /* Badges de Source & Tags */
    .source-tag-ext { background-color: #e3f2fd; color: #1976d2; padding: 3px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; border: 1px solid #1976d2; }
    .source-tag-zip { background-color: #f3e5f5; color: #7b1fa2; padding: 3px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; border: 1px solid #7b1fa2; }
    .tag-free { background-color: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }
    .tag-account { background-color: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }

    /* Cartes Candidats */
    .bannette-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #ddd; }
    .border-top { border-left-color: #2e7d32 !important; }
    .border-chance { border-left-color: #F3812B !important; }
    
    .instruction-note { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00E5FF; margin-bottom: 20px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DONNÉES INTERNATIONALES ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", "Português", 
    "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", 
    "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", 
    "Suédois", "Indonésien"
]

DIFFUSEURS = {
    "France 🇫🇷": {"France Travail": "Inclus", "Apec": "Inclus", "Hellowork": "Compte Pro", "Leboncoin": "Compte Pro"},
    "Madagascar 🇲🇬": {"PortalJob-mga": "Compte Pro", "Mada-Travail": "Inclus", "Tanajob": "Inclus"},
    "USA 🇺🇸": {"Dice": "Compte Pro", "Monster": "Compte Pro", "ZipRecruiter": "Compte Pro"},
    "International 🌐": {"LinkedIn Pro": "Compte Pro", "Indeed": "Inclus", "Remote.com": "Compte Pro"}
}

# --- 3. CONNEXION SUPABASE ---
try:
    supabase = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
except:
    st.error("Configuration Supabase manquante.")

if 'user' not in st.session_state: st.session_state.user = None

# --- 4. ACCUEIL & AUTHENTIFICATION ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)
    with col_l:
        with st.expander("🔑 Accès Utilisateur (Recruteur ou Candidat)", expanded=True):
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            role = st.radio("Je suis un :", ["Employeur",
