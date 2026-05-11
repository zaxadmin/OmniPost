import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURATION IA SÉCURISÉE ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Configuration IA manquante dans les Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS AVANCÉ (TEXTES BLANCS & LOOK ZAXX) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #001529 0%, #002147 50%, #0a3d62 100%);
        color: white !important;
    }

    /* Force le texte blanc sur tous les éléments */
    .stApp, p, span, label, div, h1, h2, h3 {
        color: white !important;
    }

    /* Conteneurs de modules */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
    }

    /* Logo et Slogan */
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #00E5FF !important; text-align: center; margin: 0; }
    .power-title { text-align: center; color: #FFFFFF !important; font-size: 16px; text-transform: uppercase; letter-spacing: 3px; }
    
    /* Bouton Premium Cyan */
    .pay-btn > div > button {
        background-color: #00E5FF !important; 
        color: #002147 !important; 
        border: none !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 70px !important;
        width: 100%;
        border-radius: 15px !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
    }
    
    /* Boutons standards (Bordure Cyan, Texte Blanc) */
    .stButton>button {
        border-radius: 10px !important;
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #00E5FF !important;
    }
    .stButton>button:hover {
        background-color: #00E5FF !important;
        color: #002147 !important;
    }

    /* Style des Alertes (fond sombre pour texte blanc) */
    .stAlert {
        background-color: rgba(0, 33, 71, 0.8) !important;
        border: 1px solid #00E5FF !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS ---
def extraire_texte_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "".join([page.extract_text() for page in pdf.pages])

def generer_pdf_cv(texte):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    t = texte.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, t)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION & 20 LANGUES ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", 
    "Português", "Mandarin", "Japonais", "Arabe", "Russe", 
    "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", 
    "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"
]

if 'user' not in st.session_state: st.session_state.user = None
if 'validite' not in st.session_state: st.session_state.validite = None
if 'footer_view' not in st.session_state: st.session_state.footer_view = None

# --- 6. HEADER ---
col_l, _ = st.columns([1, 4])
with col_l:
    st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

# --- 7. AUTHENTIFICATION ---
if not st.session_state.user:
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
    with col_logo_2:
        if os.path.exists("_20260511_163213.JPG"):
            st.image("_20260511_163213.JPG", use_column_width=True)
        else:
            st.markdown('<p class="main-logo-text">zipngo👍</p>', unsafe_allow_html=True)
        st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    with t1:
        e = st.text_input("Email", key="l_em")
        st.text_input("Mot de passe", type="password")
        if st.button("Se connecter 👍"):
            st.session_state.user, st.session_state.role = e, "Candidat"
            st.rerun()
    with t2:
        ne = st.text_input("Email", key="r_em")
        nr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("S'inscrire 🚀"):
            st.session_state.user, st.session_state.role = ne, nr
            st.rerun()

# --- 8. DASHBOARD & VALIDITÉ ---
else:
    with st.sidebar:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Déconnexion"):
            st.session_state.clear(); st.rerun()

    if st.session_state.validite is None:
        st.subheader("🚀 Activation de l'espace")
        c1, c2 = st.columns(2)
        with c1:
            d = "1 jour" if st.session_state.role == "Candidat" else "7 jours"
            if st.button(f"🎁 Essai
