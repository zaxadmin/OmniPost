import streamlit as st
from groq import Groq
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & IA ---
st.set_page_config(page_title="zipngo.zaxx | Recrutement Remote", layout="wide", page_icon="🚀")
client_ia = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. FONCTION POUR LE LOGO OFFICIEL ---
def render_logo():
    logo_path = "logo-zipngo.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        # Fallback élégant si le fichier est absent
        st.markdown("<h1 style='text-align: center; color: #00E5FF;'>zipngo<span style='color: white;'>.zaxx</span></h1>", unsafe_allow_html=True)

# --- 3. STYLE CSS (Néon & Modernité) ---
st.markdown("""
<style>
    .stApp { background-color: #0A0F1E; color: #FFFFFF; }
    .stButton>button { 
        background: #00E5FF !important; 
        color: #0A0F1E !important; 
        font-weight: 800; 
        border-radius: 8px; 
        border: none;
    }
    .stTabs [data-baseweb="tab"] { color: #FFFFFF !important; }
    .stTabs [aria-selected="true"] { color: #00E5FF !important; border-bottom-color: #00E5FF !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. DICTIONNAIRE DES 20 LANGUES ---
LANGS = {
    "Français": {
        "switch": "Vous êtes ?", "cand": "Candidat", "rec": "Recruteur", "login": "Connexion au Studio",
        "buy_c": "Pass 90j - 3 €", "buy_r": "Pass 90j - 39 €", "veille": "⚠️ PROFIL EN VEILLE"
    },
    "English": {
        "switch": "I am a:", "cand": "Candidate", "rec": "Recruiter", "login": "Login to Studio",
        "buy_c": "90d Pass - 3 €", "buy_r": "90d Pass - 39 €", "veille": "⚠️ PROFILE ON STANDBY"
    },
    "Malagasy": {
        "switch": "Iza ianao ?", "cand": "Mpmitady asa", "rec": "Mpanome asa", "login": "Hiditra",
        "buy_c": "Pass 90j - 3 €", "buy_r": "Pass 90j - 39 €", "veille": "⚠️ MOMBA ANAO MIATO"
    }
    # Les autres langues suivent la même structure...
}

if "auth" not in st.session_state: st.session_state.auth = False

# --- 5. PAGE DE CONNEXION ---
if not st.session_state.auth:
    col_l, col_mid, col_r = st.columns([1, 1.5, 1])
    with col_mid:
        render_logo()
        L_key = st.selectbox("🌐 Langue / Language", list(LANGS.keys()))
        L = LANGS[L_key]

        with st.container(border=True):
            role_choice = st.radio(L["switch"], [L["cand"], L["rec"]], horizontal=True)
            u = st.text_input("Email")
            p = st.text_input("Code ZAXX", type="password")
            
            if st.button(L["login"], use_container_width=True):
                st.session_state.update({"auth": True, "lang": L_key, "user": u, "role": role_choice, "is_expired": True})
                st.rerun()
    
    st.caption("<center>© 2026 zipngo.zaxx | Par Liliane RAKOTOBE</center>", unsafe_allow_html=True)

# --- 6. INTERFACES APRÈS CONNEXION ---
else:
    L = LANGS[st.session_state.lang]
    role_user = st.session_state.role

    with st.sidebar:
        render_logo()
        st.divider()
        if L["cand"] in role_user:
            st.info("⏱️ Essai 1 jour")
            if st.button(L["buy_c"]): st.session_state.is_expired = False; st.rerun()
        else:
            st.info("⏱️ Essai 7 jours")
            if st.button(L["buy_r"]): st.success("Accès Recruteur activé !")
        
        if st.button("🔒 Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- PORTAIL CANDIDAT ---
    if L["cand"] in role_user:
        st.title(f"🚀 Studio {L['cand']}")
        if st.session_state.is_expired:
            st.error(f"### {L['veille']}")
            st.write("Votre profil est invisible. Réactivez votre pass pour 3 € dans la barre latérale.")
        else:
            st.success("Votre profil est actif et visible mondialement.")

    # --- PORTAIL RECRUTEUR ---
    else:
        st.title(f"💼 Espace {L['rec']}")
        st.subheader("Candidats Disponibles (zipngo.zaxx)")
        st.table([{"ID": "ZAXX-A1", "Matching": "98%", "Statut": "Disponible"}])
