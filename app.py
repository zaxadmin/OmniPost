import streamlit as st
import base64
from groq import Groq
import os
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & IA ---
st.set_page_config(page_title="Zipngo-Zaxx | Recrutement & Relooking", layout="wide", page_icon="🚀")
client_ia = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. LOGO EN CODE (Base64) ---
# Injectez ici votre code Base64 pour que l'app soit autonome
LOGO_BASE64 = "VOTRE_CODE_BASE64_ZIPNGO" 

def render_logo(size=180):
    st.markdown(f'<center><img src="data:image/png;base64,{LOGO_BASE64}" width="{size}"></center>', unsafe_allow_html=True)

# --- 3. DICTIONNAIRE DES LANGUES (Extensible à 20) ---
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
if "view" not in st.session_state: st.session_state.view = "login"

# --- 5. PAGE DE CONNEXION ---
if not st.session_state.auth:
    render_logo()
    
    # Sélecteur de langue immédiat (Priorité absolue)
    L_key = st.selectbox("🌐 Choisir la langue / Select Language", list(LANGS.keys()))
    L = LANGS[L_key]

    if st.session_state.view == "login":
        with st.container(border=True):
            role_choice = st.radio(L["switch"], [L["cand"], L["rec"]], horizontal=True)
            u = st.text_input("Email / Identifiant")
            p = st.text_input("Code ZAXX", type="password")
            
            if st.button(L["login_btn"], use_container_width=True):
                # Simulation d'expiration pour le test de la mise en veille
                st.session_state.update({
                    "auth": True, 
                    "lang": L_key, 
                    "user": u, 
                    "role": role_choice,
                    "is_expired": True # On simule une expiration pour montrer le blocage
                })
                st.rerun()
        
        col_f, col_c = st.columns(2)
        if col_f.button("🔑 Code perdu ?"): st.info("Vérifiez vos emails.")
        if col_c.button("⚖️ CGU / CGV"): st.write("Propriété de Liliane RAKOTOBE. Anonymat ZAXX garanti.")

# --- 6. INTERFACES APRÈS CONNEXION ---
else:
    L = LANGS[st.session_state.lang]
    role_user = st.session_state.role

    # Sidebar dynamique selon le profil
    st.sidebar.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="100"></div>', unsafe_allow_html=True)
    
    if L["cand"] in role_user:
        st.sidebar.info(f"⏱️ {L['trial_c']}")
        if st.sidebar.button(L["buy_c"]):
            st.session_state.is_expired = False
            st.sidebar.success("Profil Activé pour 90 jours !")
    else:
        st.sidebar.info(f"⏱️ {L['trial_r']}")
        if st.sidebar.button(L["buy_r"]):
            st.sidebar.success("Accès Recruteur payé (39 €) !")

    # --- PORTAIL CANDIDAT ---
    if L["cand"] in role_user:
        st.title(f"🚀 Studio Candidat")
        
        if st.session_state.is_expired:
            with st.container(border=True):
                st.error(f"### {L['veille_title']}")
                st.write(L["veille_txt"])
                st.info("Utilisez le bouton dans la barre latérale pour réactiver votre visibilité mondiale.")
        else:
            t1, t2 = st.tabs([L["relook"], "⏳ Mon Suivi Dispatch"])
            with t1:
                st.subheader("Production & Anonymisation")
                st.file_uploader("Chargez votre CV (PDF)", type="pdf")
                if st.button(L["send"]):
                    with st.spinner("IA ZAXX en cours..."):
                        st.success("CV relooké et envoyé dans les tiroirs mondiaux !")
            with t2:
                st.write("Votre profil est actuellement dans le **Tiroir Top Priorité** de 3 recruteurs.")

    # --- PORTAIL RECRUTEUR ---
    else:
        st.title(f"💼 Espace Recruteur")
        t1, t2 = st.tabs([L["tiroir"], "✍️ Rédiger une Offre IA"])
        
        with t1:
            st.subheader("Candidats Actifs (Non-Veille)")
            st.table([
                {"ID_ZAXX": "ZAXX-A1", "Matching": "98%", "Remote": "100%"},
                {"ID_ZAXX": "ZAXX-B5", "Matching": "84%", "Remote": "100%"}
            ])
            st.caption("Les candidats en veille ne sont pas affichés.")
            
        with t2:
            st.subheader("Générateur d'offres IA")
            poste = st.text_input("Métier recherché")
            if st.button("Lancer la rédaction"):
                st.write(f"L'IA rédige une offre pro pour {poste}...")

    if st.sidebar.button("🔒 Déconnexion"):
        st.session_state.clear()
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Zipngo-Zaxx | Liliane RAKOTOBE")
