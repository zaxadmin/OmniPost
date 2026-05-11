import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. INJECTION DU DESIGN (CSS) ---
# C'est ce bloc qui transforme le texte brut en design visuel
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    /* Typographie générale */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }

    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin-bottom: 0px; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Boutons Personnalisés */
    .stButton>button { 
        background-color: #002147 !important; 
        color: white !important; 
        border-radius: 10px !important; 
        border: none !important; 
        transition: 0.3s; 
        width: 100%; 
        font-weight: bold; 
        height: 45px; 
    }
    .stButton>button:hover { 
        background-color: #F3812B !important; 
        transform: scale(1.02); 
    }

    /* Footer Design */
    .footer-container { border-top: 1px solid #eee; margin-top: 50px; padding-top: 20px; }
    .footer-text { font-size: 12px; color: #888888; text-align: center; }
    .footer-icon { color: #F3812B; font-size: 20px; vertical-align: middle; margin-left: 8px; transition: 0.3s; text-decoration: none; }
    .footer-icon:hover { color: #002147; transform: scale(1.2); }
    
    /* Suppression bordures expander */
    .stExpander { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE DES LANGUES ---
LANGS = {
    "Français 🇫🇷": {"cand": "Essai 1 jour : 1 relooking IA et 1 test ATS.", "emp": "Essai 7 jours : Accès talents et visio."},
    "English 🇺🇸": {"cand": "1-day trial: 1 AI makeover and 1 ATS test.", "emp": "7-day trial: Talent access and video."},
    "Malagasy 🇲🇬": {"cand": "Andrana 1 andro: Fanavaozana 1 sy fizahana ATS 1.", "emp": "Andrana 7 andro: Tahiry sy horonantsary."},
    "Español 🇪🇸": {"cand": "Prueba de 1 día: 1 rediseño IA y 1 test ATS.", "emp": "Prueba de 7 días: Acceso y video."}
}

# --- 4. INTERFACE UTILISATEUR ---
if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    # Barre de langue
    col_l, _ = st.columns([1, 2])
    with col_l:
        sel_lang = st.selectbox("🌐 Language", list(LANGS.keys()))
    
    # Logo & Titre
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cartes de présentation
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div style="background:white; padding:20px; border-radius:15px; border:1px solid #eee; text-align:center;">
            <h3 style="color:#002147;">Candidat</h3><p>{LANGS[sel_lang]['cand']}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="background:white; padding:20px; border-radius:15px; border:1px solid #eee; text-align:center;">
            <h3 style="color:#002147;">Employeur</h3><p>{LANGS[sel_lang]['emp']}</p>
        </div>""", unsafe_allow_html=True)

    # Inscription / Connexion
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Connexion", "📝 Inscription"])
    with t2:
        st.text_input("Email", key="reg_e")
        st.button("Démarrer mon essai 👍")

# --- 5. FOOTER JURIDIQUE ---
st.markdown('<div class="footer-container"></div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)

with f1:
    with st.expander("⚖️ Mentions Légales"):
        st.write("**Éditeur :** RAKOTOBE Liliane. Propriété exclusive.")
with f2:
    with st.expander("📜 CGV"):
        st.write("**Paiement :** Immédiat. Pas de remboursement pour produit virtuel.")
with f3:
    st.markdown(f"""
        <div class="footer-text">
            © 2026 <b>RAKOTOBE Liliane</b> | 
            <a href="mailto:creationsites06@gmail.com" class="footer-icon">
                <i class="fa-regular fa-envelope"></i>
            </a>
        </div>
    """, unsafe_allow_html=True)
