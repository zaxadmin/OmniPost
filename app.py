import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# CORRECTION : Injection CSS avec les balises HTML nécessaires
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    /* Typographie et Couleurs */
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin-bottom: 0px; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    
    /* Cartes */
    .feature-card { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 1px solid #e1f5fe; box-shadow: 0 10px 20px rgba(0, 33, 71, 0.05); text-align: center; margin-bottom: 20px; }
    
    /* Boutons personnalisés */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: scale(1.01); }

    /* Footer */
    .footer-container { border-top: 1px solid #eee; margin-top: 50px; padding-top: 20px; }
    .footer-text { font-size: 11px; color: #888888; text-align: center; }
    .footer-icon { color: #F3812B; font-size: 18px; vertical-align: middle; margin-left: 5px; transition: 0.3s; text-decoration: none; }
    .footer-icon:hover { transform: scale(1.2); color: #002147; }
    
    /* Nettoyage expander */
    .stExpander { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. TRADUCTIONS ---
LANGS = {
    "Français 🇫🇷": {"cand": "Essai 1 jour : 1 relooking IA et 1 test ATS.", "emp": "Essai 7 jours : Accès talents et visio."},
    "English 🇺🇸": {"cand": "1-day trial: 1 AI makeover and 1 ATS test.", "emp": "7-day trial: Talent access and video."},
    "Malagasy 🇲🇬": {"cand": "Andrana 1 andro: Fanavaozana 1 sy fizahana ATS 1.", "emp": "Andrana 7 andro: Tahiry sy horonantsary."},
    "Español 🇪🇸": {"cand": "Prueba de 1 día: 1 rediseño IA y 1 test ATS.", "emp": "Prueba de 7 días: Acceso y video."}
}

# --- 3. CONNEXIONS (Secrets) ---
# Assure-toi que ces noms correspondent à tes secrets sur Streamlit Cloud
try:
    supabase_auth = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
except:
    st.warning("Configuration Supabase manquante dans les secrets.")

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. ACCUEIL ---
if not st.session_state.user:
    # Sélecteur de langue
    c_l, _ = st.columns([1, 2])
    with c_l:
        sel_lang = st.selectbox("🌐 Language", list(LANGS.keys()))
    
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="feature-card"><h2 style="color:#002147;">Candidat</h2><p>{LANGS[sel_lang]["cand"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="feature-card"><h2 style="color:#002147;">Employeur</h2><p>{LANGS[sel_lang]["emp"]}</p></div>', unsafe_allow_html=True)

    t_log, t_reg = st.tabs(["🔑 Connexion", "📝 Inscription"])
    
    with t_reg:
        re = st.text_input("Email", key="reg_email")
        rp = st.text_input("Mot de passe", type="password", key="reg_pass")
        if st.button("S'inscrire gratuitement 👍"):
            st.success("Compte créé (Simulation). Connectez-vous !")

    with t_log:
        le = st.text_input("Email", key="log_email")
        lp = st.text_input("Pass", type="password", key="log_pass")
        if st.button("Se connecter 👍"):
            st.session_state.user = le
            st.rerun()

# --- 5. FOOTER (FIXÉ) ---
st.markdown('<div class="footer-container"></div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)

with f1:
    with st.expander("⚖️ Mentions Légales"):
        st.write("Éditeur : RAKOTOBE Liliane. Propriété exclusive.")

with f2:
    with st.expander("📜 CGV"):
        st.write("Services numériques. Pas de remboursement après exécution.")

with f3:
    st.markdown(f"""
        <div class="footer-text">
            © 2026 <b>RAKOTOBE Liliane</b> | 
            <a href="mailto:creationsites06@gmail.com" class="footer-icon">
                <i class="fa-regular fa-envelope"></i>
            </a>
        </div>
    """, unsafe_allow_html=True)
