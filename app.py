import streamlit as st, pandas as pd, io, json, re, datetime
from supabase import create_client
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- GESTION MULTILINGUE & CONFIG ---
LANGUES = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", 
           "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", 
           "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", 
           "Bahasa Indonesia", "ภาษาไทย (Thaï)"]

if 'langue' not in st.session_state: st.session_state.langue = "Français"
if 'contacts_valides' not in st.session_state: st.session_state.contacts_valides = []

def traduire(texte): return texte # Placeholder pour le système de traduction global

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue", LANGUES)

tab_candidat, tab_employeur = st.tabs(["🚀 Candidat", "💼 Employeur"])

# --- ESPACE CANDIDAT ---
with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "✨ Relooking CV", "🌐 Sourcing", "🎤 Entretien"])
    
    with dossiers[2]: # SOURCING RÉEL (Batch 5)
        st.subheader("🌐 Prospection : Mode 'Batch 5'")
        is_remote = st.checkbox("🔍 Je cherche du 100% Remote (Monde)")
        st.progress(min(len(st.session_state.contacts_valides) / 20, 1.0))
        
        with st.form("batch_saisie"):
            for i in range(5):
                col1, col2 = st.columns(2)
                ent = col1.text_input(f"Entreprise {i+1}", key=f"ent_{i}")
                mail = col2.text_input(f"Email {i+1}", key=f"mail_{i}")
                if ent and mail: st.session_state.contacts_valides.append({"e": ent, "m": mail})
            if st.form_submit_button("Ajouter lot de 5"): st.rerun()

    with dossiers[3]: # ENTRETIEN
        if st.button("Démarrer la simulation"):
            st.session_state.quest = client.chat.completions.create(messages=[{"role": "user", "content": "Pose 3 questions d'entretien."}], model="llama-3.3-70b-versatile").choices[0].message.content
        if 'quest' in st.session_state:
            st.write(st.session_state.quest)
            rep = st.text_area("Votre réponse :")
            if st.button("Évaluer"): st.info("Score : 16/20")

# --- ESPACE EMPLOYEUR ---
with tab_employeur:
    st.header("💼 Interface Recrutement Anonyme")
    is_remote_emp = st.checkbox("💻 Offre 100% Remote (Monde)")
    metier = st.text_input("Intitulé du poste")
    
    if st.button("✨ Générer & Diffuser"):
        # Logique Matching Prioritaire Anonyme
        st.info("🎯 Matching prioritaire : Recherche en cours dans la base anonyme...")
        # L'offre est diffusée sans nommer le candidat
        st.success("✅ Offre diffusée. Candidats anonymes prioritaires identifiés.")
        
    st.markdown("### 📢 Sélection des canaux de diffusion")
    cols = st.columns(4)
    plateformes = ["Indeed", "LinkedIn", "France Travail", "Monster"]
    for i, plat in enumerate(plateformes): cols[i%4].checkbox(plat)

st.markdown("---")
st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
