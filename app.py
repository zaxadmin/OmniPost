import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
from datetime import datetime, timedelta
import hashlib
import os

# --- 1. CONFIGURATION ---
try:
    client_ia = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
except:
    st.error("Clé API manquante.")

st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS PREMIUM ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(160deg, #001529 0%, #002147 100%); color: white !important; }
    .stButton>button { border: 1px solid #00E5FF !important; color: white !important; background: transparent; width: 100%; font-weight: bold; }
    .stButton>button:hover { background: #00E5FF !important; color: #002147 !important; }
    p, span, label, h1, h2, h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALISATION ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. PORTAIL D'ACCÈS ---
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Affichage du logo zipngo-zaxx avec slogan Power of Choice
        if os.path.exists("logo_zipngo_4.jpg"):
            st.image("logo_zipngo_4.jpg", use_column_width=True)
        else:
            st.markdown('<h1 style="color:#00E5FF; text-align:center;">zipngo-zaxx👍</h1>', unsafe_allow_html=True)
            st.markdown('<p style="text-align:center; letter-spacing:3px;">THE POWER OF CHOICE</p>', unsafe_allow_html=True)

    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    with t1:
        u = st.text_input("Email").lower()
        p = st.text_input("Clé d'accès", type="password")
        c1, c2 = st.columns(2)
        if c1.button("Accès Recruteur"):
            st.session_state.update({"auth":True, "user":u, "role":"Employeur"}); st.rerun()
        if c2.button("Accès Candidat"):
            st.session_state.update({"auth":True, "user":u, "role":"Candidat"}); st.rerun()

# --- 5. DASHBOARD ---
else:
    st.sidebar.image("logo_zipngo_4.jpg") if os.path.exists("logo_zipngo_4.jpg") else st.sidebar.title("Zipngo-Zaxx")
    if st.sidebar.button("Déconnexion"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.role == "Candidat":
        st.header("🚀 IA Production")
        f = st.file_uploader("CV PDF", type="pdf")
        if f and st.button("✨ Relooking IA"):
            st.info("Traitement IA en cours...")
    else:
        st.header("📂 Flux Recruteur")
        st.table([{"ID": "CAND-001", "Match": "98%", "Statut": "🔒 Masqué"}])

# --- 6. FOOTER ---
st.divider()
st.markdown('<p style="text-align:center; font-size:12px; color:#00E5FF;">© 2026 Zipngo-Zaxx | Système Autonome | Liliane RAKOTOBE</p>', unsafe_allow_html=True)
