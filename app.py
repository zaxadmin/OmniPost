import streamlit as st
from supabase import create_client
from ai_engine import coach_ia, generate_offer
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

st.markdown("""
    <style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin-bottom: 0px; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; }
    .feature-card { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 1px solid #e1f5fe; box-shadow: 0 10px 20px rgba(0, 33, 71, 0.05); height: 100%; }
    .price-tag { background-color: #002147; color: #00E5FF; padding: 5px 15px; border-radius: 20px; font-weight: bold; display: inline-block; margin-top: 10px; }
    .fake-payment { background-color: #f0f7ff; border: 1px dashed #002147; padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center; }
    
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #F3812B !important; transform: scale(1.01); }
    </style>
""", unsafe_allow_html=True)

# --- 2. DICTIONNAIRE DES 20 LANGUES ---
LANGS = {
    "Français 🇫🇷": "French", "English 🇺🇸": "English", "Malagasy 🇲🇬": "Malagasy", 
    "Español 🇪🇸": "Spanish", "Deutsch 🇩🇪": "German", "Italiano 🇮🇹": "Italian", 
    "Português 🇧🇷": "Portuguese", "Русский 🇷🇺": "Russian", "日本語 🇯🇵": "Japanese", 
    "العربية 🇸🇦": "Arabic", "Türkçe 🇹🇷": "Turkish", "Nederlands 🇳🇱": "Dutch",
    "한국어 🇰🇷": "Korean", "中文 🇨🇳": "Chinese", "हिन्दी 🇮🇳": "Hindi", 
    "Polski 🇵🇱": "Polish", "Svenska 🇸🇪": "Swedish", "Tiếng Việt 🇻🇳": "Vietnamese",
    "Bahasa Indonesia 🇮🇩": "Indonesian", "ไทย 🇹🇭": "Thai"
}

# --- 3. CONNEXIONS SUPABASE ---
supabase_auth = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
supabase_data = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

# --- 4. ACCUEIL & INSCRIPTION ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0; color: #F3812B; font-size: 80px;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f'<div class="feature-card"><h3 style="color:#002147;">👨‍🚀 Candidat</h3><div class="price-tag">3€ / 3 mois</div><p>Accès multilingue au Coach IA et aux recruteurs.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="feature-card"><h3 style="color:#002147;">💼 Employeur</h3><div class="price-tag">49€ / 3 mois</div><p>Recherche par localisation et visio Zaxx intégrée.</p></div>', unsafe_allow_html=True)

    t_log, t_reg = st.tabs(["🔑 Connexion", "📝 Inscription"])
    with t_reg:
        re = st.text_input("Email", key="re")
        rp = st.text_input("Pass", type="password", key="rp")
        rr = st.radio("Type de compte", ["Candidat", "Employeur"], horizontal=True)
        st.markdown(f'<div class="fake-payment">💳 <b>Paiement : {"3€" if rr=="Candidat" else "49€"}</b><br><small>Pas de remboursement. Accès 90 jours.</small></div>', unsafe_allow_html=True)
        if st.button("Valider et S'inscrire 👍"):
            exp = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
            supabase_auth.table("users").insert({"email": re, "password": rp, "role": rr, "expire_at": exp}).execute()
            st.success("Compte activé !")

    with t_log:
        le, lp = st.text_input("Email", key="le"), st.text_input("Pass", type="password", key="lp")
        if st.button("Se connecter 👍"):
            res = supabase_auth.table
