import streamlit as st
import datetime
import pandas as pd
import io
import re
import json
import urllib.parse
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
except:
    st.error("Erreur de configuration.")

if 'user_email' not in st.session_state: st.session_state.user_email = "test@exemple.com"

# --- CONSTANTES ---
LANGUES_DISPONIBLES = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"]

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

# Barre Latérale
with st.sidebar:
    st.session_state.langue = st.selectbox("🌐 Langue", LANGUES_DISPONIBLES)
    cgv_accept = st.checkbox("J'accepte les Conditions Générales de Vente (CGV)")
    st.markdown("---")
    st.link_button("🚀 Candidat (6€ / 3 mois)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    st.link_button("💼 Recruteur (39€ / mois)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

# --- ESPACE CANDIDAT (Avec tous les tiroirs) ---
with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "📅 Mes Entretiens"])
    with dossiers[2]: # Relooking
        st.subheader("✨ Relooking CV")
        if st.button("🚀 Lancer l'optimisation IA"):
            if cgv_accept: st.success("Optimisation lancée.")
            else: st.error("Veuillez accepter les CGV.")
    with dossiers[4]: # Entretiens
        if st.button("Confirmer et lever l'anonymat"):
            if cgv_accept: st.success("Anonymat levé.")
            else: st.error("Veuillez accepter les CGV.")

# --- ESPACE EMPLOYEUR (Avec tous les tiroirs) ---
with tab_employeur:
    tiroirs = st.tabs(["🔥 Matchs", "📂 Vivier", "👤 Profils", "📅 Entretiens", "🗄️ Archives"])
    with tiroirs[0]: # Matchs
        st.subheader("🔥 Fiches Candidats")
        if st.button("👍 Offrir Entretien", key="ent_1"):
            if cgv_accept: st.success("Entretien proposé !")
            else: st.error("Acceptez les CGV.")
        if st.button("👍 Lever l'anonymat", key="anon_1"):
            if cgv_accept: st.success("Anonymat levé.")
            else: st.error("Acceptez les CGV.")
    with tiroirs[3]: # Entretiens
        st.subheader("📅 Planning Entretiens")
        # Logique de gestion des feedback ici...

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """<div style='text-align: center;'>
        <p>zipngo 2026 - Système complet | Créé par <b>Liliane RAKOTOBE</b></p>
        <p>Contact : <a href='mailto:creationsites06@gmail.com'>📧 creationsites06@gmail.com</a></p>
    </div>""", unsafe_allow_html=True
)
