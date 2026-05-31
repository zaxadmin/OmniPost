import streamlit as st
import datetime
import pandas as pd
import io
import json
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

# --- FONCTIONS D'ORIGINE ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis en {langue_cible}. Renvoie uniquement le texte : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse pour le poste '{metier}'. Retourne JSON: 'header', 'sidebar', 'main', 'mots_cles_ajoutes'. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("```", ""))

def appliquer_design_geometrique(pdf, data):
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255); pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, data['header']['nom'], ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, data['header']['titre_poste'], ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, data['main']['titre'], ln=True)

# --- MOTEUR DE TRI AUTO ---
def trier_candidats_auto(offre_data):
    profils = supabase.table("candidats").select("*").execute().data
    for p in profils:
        prompt = f"Compare le CV: {p.get('cv_text')} et l'Offre: {offre_data}. Score 0-100. JSON: {{"score": 0}}"
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        score = json.loads(res.choices[0].message.content).get('score', 0)
        statut = "Matchs" if score >= 50 else "Vivier"
        supabase.table("candidats").update({"statut": statut, "score": score}).eq("id", p['id']).execute()

# --- AUTHENTIFICATION ---
if 'user_email' not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>Bienvenue sur zipngo</h1>", unsafe_allow_html=True)
    st.markdown("L'IA au service de votre carrière. Connectez-vous pour commencer.")
    st.text_input("Email", key="login_email")
    if st.button("Se connecter"):
        st.session_state.user_email = st.session_state.login_email
        st.rerun()
    st.stop()

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.session_state.langue = st.sidebar.selectbox("🌐 Langue", ["Français", "English (US)", "Malagasy"])
cgv_accept = st.sidebar.checkbox("J'accepte les CGV")

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[2]: # Relooking
        metier = st.text_input("Poste visé")
        up = st.file_uploader("Upload CV", type=["pdf"])
        if up and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            st.download_button("⬇️ Télécharger CV", data=pdf.output(dest='S').encode('latin-1'), file_name="CV.pdf")

with tab_employeur:
    tiroirs = st.tabs(["🔥 Matchs", "📂 Vivier", "👤 Profils", "📅 Entretiens", "🗄️ Archives"])
    with tiroirs[0]: # Publication & Scan Auto
        metier = st.text_input("Intitulé du poste")
        lieu = st.text_input("Lieu")
        remote = st.checkbox("Remote")
        if st.button("✨ Publier et Scanner"):
            trier_candidats_auto({"metier": metier, "lieu": lieu, "remote": remote})
            st.success("Analyse terminée. Matchs et Vivier mis à jour.")
    
    with tiroirs[0]: # Matchs
        for c in supabase.table("candidats").select("*").gte("score", 50).execute().data:
            if st.button(f"👍 Entretien avec {c['nom_candidat']}"): pass

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align:center;'>Créé par <b>Liliane RAKOTOBE</b> | <a href='mailto:creationsites06@gmail.com'>📧</a></div>", unsafe_allow_html=True)
