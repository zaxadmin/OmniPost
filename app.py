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

# --- AUTHENTIFICATION AVEC TEXTES ---
if 'user_email' not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#000080;'>Bienvenue sur zipngo</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center; padding: 20px; font-size: 1.2em;'>
        <p><b>L'intelligence artificielle au service de votre trajectoire professionnelle.</b></p>
        <p>Zipngo est la plateforme premium qui connecte les talents aux meilleures opportunités avec une sécurité totale.</p>
        <p><b>Candidats :</b> Optimisez votre CV, sourcez vos entreprises et gérez vos entretiens dans un environnement sécurisé.</p>
        <p><b>Recruteurs :</b> Diffusez vos offres, gérez votre vivier et levez l'anonymat de vos futurs collaborateurs grâce à notre système de matching unique.</p>
    </div>
    """, unsafe_allow_html=True)
    st.text_input("Veuillez saisir votre email pour accéder à votre espace :", key="login_email")
    if st.button("Se connecter"):
        st.session_state.user_email = st.session_state.login_email
        st.rerun()
    st.stop()

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

# Barre Latérale
with st.sidebar:
    st.session_state.langue = st.selectbox("🌐 Sélectionner la langue", ["Français", "English (US)", "Malagasy"])
    cgv_accept = st.checkbox("J'accepte les Conditions Générales de Vente (CGV)")
    st.markdown("---")
    st.link_button("🚀 Candidat (6€ / 3 mois)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    st.link_button("💼 Recruteur (39€ / mois)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Espace Candidat", "💼 Espace Recruteur"])

# --- ONGLET CANDIDAT ---
with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "📅 Mes Entretiens"])
    with dossiers[2]: # Relooking
        st.subheader("✨ Relooking de votre CV par IA")
        st.write("Téléchargez votre CV actuel pour obtenir une version optimisée et adaptée au marché.")
        if st.button("🚀 Lancer l'optimisation IA"):
            if cgv_accept: st.success("Analyse en cours, votre nouveau CV sera prêt sous peu.")
            else: st.error("Veuillez accepter les CGV dans la barre latérale pour continuer.")
    with dossiers[4]: # Entretiens
        st.subheader("📅 Gestion de mes Entretiens")
        st.write("Visualisez ici vos propositions d'entretiens. Confirmez votre créneau pour lever l'anonymat.")
        if st.button("Confirmer et lever l'anonymat"):
            if cgv_accept: st.success("Entretien validé. Coordonnées échangées avec le recruteur.")
            else: st.error("Veuillez accepter les CGV.")

# --- ONGLET EMPLOYEUR ---
with tab_employeur:
    tiroirs = st.tabs(["🔥 Matchs", "📂 Vivier", "👤 Profils", "📅 Entretiens", "🗄️ Archives"])
    with tiroirs[0]: # Matchs
        st.subheader("🔥 Candidats en attente de traitement")
        st.write("Consultez les fiches anonymes. Utilisez le pouce pour passer à l'étape suivante.")
        if st.button("👍 Offrir Entretien (Jitsi)", key="ent_1"):
            if cgv_accept: st.success("Entretien proposé. Créneaux envoyés au candidat.")
            else: st.error("Veuillez accepter les CGV.")
        if st.button("👍 Lever l'anonymat", key="anon_1"):
            if cgv_accept: st.success("Anonymat levé. Données personnelles partagées.")
            else: st.error("Veuillez accepter les CGV.")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """<div style='text-align: center;'>
        <p>zipngo 2026 - Système complet | Créé par <b>Liliane RAKOTOBE</b></p>
        <p>Contact : <a href='mailto:creationsites06@gmail.com'>📧 creationsites06@gmail.com</a></p>
    </div>""", unsafe_allow_html=True
)
