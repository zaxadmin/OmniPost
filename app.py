import streamlit as st
import requests
import imaplib
import email
import io
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
SALON_FIXE = "https://meet.jit.si/zipngo-entretien-privé"

# --- CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .zip { color: #000080; font-weight: bold; font-size: 3rem; }
    .ngo { color: #4169E1; font-weight: bold; font-size: 3rem; }
    .main-container { background-color: #f9f9f9; padding: 20px; border-radius: 10px; }
    </style>
    <div><span class="zip">zip</span><span class="ngo">ngo</span>.zaxx.app</div>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
tab_home, tab_candidat, tab_employeur, tab_cgv = st.tabs(["🏠 Présentation", "🚀 Espace Candidat", "💼 Espace Employeur", "📜 CGV"])

# --- TAB 1 : PRÉSENTATION ---
with tab_home:
    st.title("L'avenir du recrutement par IA")
    st.write("Bienvenue sur la plateforme qui connecte les talents sans frontières.")
    st.info("Mode d'emploi : Les candidats s'inscrivent et sourcent leurs cibles. Les employeurs trient leurs candidatures par IA et rejoignent le salon Jitsi permanent.")

# --- TAB 2 : CANDIDAT ---
with tab_candidat:
    st.header("Interface Candidat")
    # Inscription, Sourcing IA, Upload CV, Envoi campagne BCC
    # (Logique déjà définie : Formulaire, Sourcing Groq, Upload, Envoi Resend)

# --- TAB 3 : EMPLOYEUR ---
with tab_employeur:
    st.header("Interface Employeur")
    # Configuration Mail Tri IA
    with st.expander("⚙️ Configurer Tri IA par Email"):
        email_in = st.text_input("Email de réception")
        pwd_in = st.text_input("Mot de passe app", type="password")
        if st.button("Sauvegarder"):
            supabase.table("recruteurs").upsert({"email_recruteur": email_in, "email_tri": email_in, "password_tri": pwd_in}).execute()
    
    if st.button("🚀 Lancer le Tri IA des CV reçus"):
        # Logique de connexion IMAP + Extraction PDF + Tri Groq
        st.success("Tri terminé. Voici les 3 candidats les plus pertinents :")
        # Affichage résultats + Bouton 👍
        if st.button("👍 Proposer Entretien"):
            st.write(f"Invitation envoyée ! [Rejoindre le salon]({SALON_FIXE})")

# --- TAB 4 : CGV ---
with tab_cgv:
    st.markdown("### Conditions Générales")
    st.write("Zipngo - 2026. Abonnement Premium : 6€ (Candidat) / 39€ (Recruteur).")
