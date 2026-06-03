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

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium Global", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- LISTE DES 20 LANGUES ---
LANGUES = [
    "Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", 
    "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", 
    "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", 
    "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"
]

# --- FONCTION TRADUCTION IA (Supporte les 20 langues) ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

if 'langue' not in st.session_state: st.session_state.langue = "Français"
st.session_state.langue = st.sidebar.selectbox("🌐 Langue", LANGUES, index=0)

tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil", "🚀 Candidat", "💼 Employeur"]])

with tab_candidat:
    st.link_button("💎 Passer en Premium Candidat (6€)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04", type="primary")
    # ... VOTRE CODE CANDIDAT ...

with tab_employeur:
    st.link_button("💎 Passer en Premium Employeur (39€)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03", type="primary")
    # ... VOTRE CODE EMPLOYEUR ...

# --- PIED DE PAGE & CGV ENRICHIES ---
st.markdown("---")
with st.expander("⚖️ Conditions Générales de Vente (CGV)"):
    st.markdown("""
    **1. Objet :** Mise en relation anonymisée et outils de matching IA.\n
    **2. Tarifs :** Candidat (6€) / Employeur (39€). Aucun remboursement après activation.\n
    **3. Données :** Suppression sur demande sous 48h. Conformité RGPD assurée.\n
    **4. Responsabilité :** Le service est fourni tel quel. L'anonymat est levé uniquement par consentement mutuel.\n
    **5. Exécution :** Accès immédiat au service dès validation du paiement Stripe.
    """)

st.markdown(f"<div style='text-align: center;'>Application zipngo 2026 — Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
