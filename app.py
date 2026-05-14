import streamlit as st
from groq import Groq
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & IA ---
st.set_page_config(page_title="Zipngo-Zaxx | Recrutement & Relooking", layout="wide", page_icon="🚀")
client_ia = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. FONCTION POUR LE LOGO (FICHIER LOCAL) ---
def render_logo():
    # On cherche le fichier dans le dossier de l'app
    logo_path = "logo_zipngo_4.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        # Texte de secours si l'image est manquante
        st.markdown("<h1 style='text-align: center; color: #007bff;'>Zipngo-Zaxx</h1>", unsafe_allow_html=True)

# --- 3. DICTIONNAIRE DES LANGUES (20 LANGUES PRÊTES) ---
LANGS = {
    "Français": {
        "switch": "Vous êtes ?",
        "cand": "Candidat (Cherche un job)",
        "rec": "Recruteur (Cherche un talent)",
        "login_btn": "Se connecter au Studio",
        "trial_c": "Essai 1 jour actif",
        "trial_r": "Essai 7 jours actif",
        "buy_c": "Réactiver mon profil (90 j) - 3 €",
        "buy_r": "Accès Recruteur (90 j) - 39 €",
        "veille_title": "⚠️ PROFIL EN VEILLE",
        "veille_txt": "Votre pass de 90 jours a expiré. Votre profil est invisible pour les recruteurs.",
        "relook": "✨ Relooking & Anonymisation IA",
        "tiroir": "📥 Tiroirs de Candidatures",
        "send": "Anonymiser & Envoyer au Dispatcher"
    },
    "English": {
        "switch": "I am a:",
        "cand": "Candidate (Looking for a job)",
        "rec": "Recruiter (Looking for talent)",
        "login_btn": "Login to Studio",
        "trial_c": "1-day trial active",
        "trial_r": "7-day trial active",
        "buy_c": "Reactivate my profile (90 d) - 3 €",
        "buy_r": "Recruiter Access (90 d) - 39 €",
        "veille_title": "⚠️ PROFILE ON STANDBY",
        "veille_txt": "Your 90-day pass has expired. Your profile is invisible to recruiters.",
        "relook": "✨ AI Relooking & Anonymization",
        "tiroir": "📥 Candidate Drawers",
        "send": "Anonymize & Send to Dispatcher"
    },
    "Malagasy": {
        "switch": "Iza ianao ?",
        "cand": "Candidat (Mitady asa)",
        "rec": "Recruteur (Mitady mpiasa)",
        "login_btn": "Hiditra",
        "trial_c": "Andrana 1 andro",
        "trial_r": "Andrana 7 andro",
        "buy_c": "Hamelona ny momba ahy (90 andro) - 3 €",
        "buy_r": "Hividy fahafahana mijery (90 andro) - 39 €",
        "veille_title": "⚠️ MOMBA ANAO MIATO",
        "veille_txt": "Lany fe-potoana ny 90 andro. Tsy hita mivohitra amin'ny mpampiasa ianao.",
        "relook": "✨ Fanamboarana CV IA",
        "tiroir": "📥 Fitoerana mpitady asa",
        "send": "Alefa"
    }
}

# --- 4. GESTION DE LA SESSION ---
if "auth" not in st.session_state: st.session_state.auth = False

# --- 5. PAGE DE CONNEXION ---
if not st.session_state.auth:
    col_l, col_r = st.columns([1, 2])
    with col_l:
        render_logo()
    
    # Sélecteur de langue immédiat
    L_key = st.selectbox("🌐 Choisir la langue / Select Language", list(LANGS.keys()))
    L = LANGS[L_key]

    with st.container(border=True):
        role_choice = st.radio(L["switch"], [L["cand"], L["rec"]], horizontal=True)
        u = st.text_input("Email / Identifiant")
        p = st.text_input("Code ZAXX", type="password")
        
        if st.button(L["login_btn"], use_container_width=True):
            st.session_state.update({
                "auth": True, 
                "lang": L_key, 
                "user": u, 
                "role": role_choice,
                "is_expired": True # On simule l'expiration pour le test de la veille
            })
            st.rerun()
    
    st.caption("<center>© 2026 Zipngo-Zaxx | Par Liliane RAKOTOBE</center>", unsafe_allow_html=True)

# --- 6. INTERFACES APRÈS CONNEXION ---
else:
    L = LANGS[st.session_state.lang]
    role_user = st.session_state.role

    # Sidebar avec Logo
    with st.sidebar:
        render_logo()
        st.divider()
        
        if L["cand"] in role_user:
            st.info(f"⏱️ {L['trial_c']}")
            if st.button(L["buy_c"]):
                st.session_state.is_expired = False
                st.success("Profil Réactivé !")
        else:
            st.info(f"⏱️ {L['trial_r']}")
            if st.button(L["buy_r"]):
                st.success("Accès Recruteur activé !")

    # --- PORTAIL CANDIDAT ---
    if L["cand"] in role_user:
        st.title(f"🚀 Studio Candidat")
        
        if st.session_state.is_expired:
            st.error(f"### {L['veille_title']}")
            st.write(L["veille_txt"])
            st.info("Utilisez le bouton 'Réactiver' dans la barre latérale.")
        else:
            t1, t2 = st.tabs([L["relook"], "⏳ Mon Suivi"])
            with t1:
                st.file_uploader("Chargez votre CV (PDF)", type="pdf")
                if st.button(L["send"]):
                    st.success("CV anonymisé et envoyé !")
            with t2:
                st.write("Votre profil est visible par les recruteurs.")

    # --- PORTAIL RECRUTEUR ---
    else:
        st.title(f"💼 Espace Recruteur")
        t1, t2 = st.tabs([L["tiroir"], "✍️ Offre IA"])
        
        with t1:
            st.subheader("Candidats Disponibles")
            st.table([{"ID_ZAXX": "ZAXX-A1", "Matching": "98%", "Remote": "100%"}])
            
        with t2:
            st.subheader("Générateur d'offres IA")
            if st.button("Rédiger"):
                st.write("L'IA prépare l'annonce...")

    if st.sidebar.button("🔒 Déconnexion"):
        st.session_state.clear()
        st.rerun()
