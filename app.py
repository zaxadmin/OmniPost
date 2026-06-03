import streamlit as st
import datetime
import pandas as pd
import io
import re
import json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
import resend
import requests
import urllib.parse

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="zipngo | ATS Premium Global", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- FONCTIONS UTILES ---
def extraire_json_propre(texte_brut):
    try:
        texte_nettoye = re.sub(r"```json|```", "", texte_brut).strip()
        return json.loads(texte_nettoye)
    except:
        match = re.search(r"\{.*\}", texte_brut, re.DOTALL)
        if match: return json.loads(match.group(0))
    return {"score": 0, "justification": "Erreur d'analyse."}

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

# Gestion des onglets
tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

# --- ONGLET CANDIDAT ---
with tab_candidat:
    # Bouton avec clé unique pour éviter le conflit
    st.link_button("💎 Passer en Premium Candidat (6€)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04", type="primary")
    
    st.subheader("📄 Configuration du Profil")
    # Utilisez des clés uniques pour chaque input
    nom_cand = st.text_input("Vrai Nom", key="cand_nom_input")
    # ... (le reste de votre logique candidat)

# --- ONGLET EMPLOYEUR ---
with tab_employeur:
    # Bouton avec clé unique différente de celle du candidat
    st.link_button("💎 Passer en Premium Employeur (39€)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03", type="primary")
    
    st.subheader("💼 Espace Recruteur")
    # ... (le reste de votre logique employeur)

# --- PIED DE PAGE ---
st.markdown("---")
st.markdown("Application gérée par **Liliane RAKOTOBE**.")
