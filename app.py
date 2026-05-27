import streamlit as st
import datetime
import pandas as pd
import io
import re
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- FONCTION TRADUCTION IA ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

# --- FONCTIONS ---
def creer_pdf_cv_pro(texte_ia, nom_fichier, style):
    pdf = FPDF()
    pdf.add_page()
    if style == "Classique": pdf.set_font("Times", 'B', 16)
    elif style == "Moderne": pdf.set_font("Arial", 'B', 18)
    else: pdf.set_font("Courier", 'B', 16)
    pdf.cell(200, 10, txt="Mon CV Optimisé", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=texte_ia)
    pdf.output(nom_fichier)

def afficher_cgv():
    texte_cgv = "1. Accès Candidat 6€/3mois | Recruteur 39€/mois. 2. Limites Gratuit : 1 CV/mois, 1 campagne/mois. 3. Premium : 3 CVs/semaine, 20 mails/jour."
    st.markdown(traduire_avec_ia(texte_cgv, st.session_state.langue))

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#333333; font-size: 14px; margin-top: 0px;'>.zaxx.app</p>", unsafe_allow_html=True)

# Sélecteur de langue
langues = ["Français", "English (US)", "Español", "中文 (Mandarin)", "العربية (Arabe)", "Deutsch"]
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue", langues, index=0)

# Présentation
st.markdown(f"<h4 style='color: #4169E1; margin: 20px 0;'>{traduire_avec_ia('L\'intelligence artificielle au service de votre trajectoire professionnelle.', st.session_state.langue)}</h4>", unsafe_allow_html=True)
st.markdown(f"<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4169E1; margin-bottom: 20px;'><h4>{traduire_avec_ia('Bienvenue sur zipngo', st.session_state.langue)}</h4>{traduire_avec_ia('Optimisez vos démarches et facilitez vos interactions professionnelles grâce à notre écosystème intelligent.', st.session_state.langue)}</div>", unsafe_allow_html=True)

with st.expander(traduire_avec_ia("📜 Lire les CGV", st.session_state.langue)): afficher_cgv()
st.checkbox(traduire_avec_ia("J'accepte les CGV", st.session_state.langue), key="accept_cgv")

# --- ONGLETS ---
tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil", "🚀 Candidat", "💼 Employeur"]])

with tab_home:
    st.write(traduire_avec_ia("Bienvenue dans votre espace d'accueil.", st.session_state.langue))

with tab_candidat:
    dossiers = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"]])
    
    with dossiers[0]:
        st.subheader(traduire_avec_ia("📜 Historique des envois", st.session_state.langue))
        try:
            response = supabase.table("sourcing").select("email, date").order("date", desc=True).execute()
            if response.data: st.table(pd.DataFrame(response.data))
        except Exception as e: st.error(f"Erreur : {e}")

    with dossiers[3]: # RELOOKING
        st.subheader(traduire_avec_ia("✨ Relooking & Scoring ATS", st.session_state.langue))
        source = st.radio(traduire_avec_ia("Source", st.session_state.langue), [traduire_avec_ia("Uploader depuis mon ordinateur", st.session_state.langue), traduire_avec_ia("Sélectionner parmi mes CVs", st.session_state.langue)])
        
        texte_cv = ""
        if "Uploader" in source:
            up = st.file_uploader(traduire_avec_ia("Upload", st.session_state.langue), type=["pdf"])
            if up: texte_cv = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
        else:
            data = supabase.table("cvs").select("nom_fichier, contenu").execute().data
            if data:
                choix = st.selectbox("Mes CVs", [c['nom_fichier'] for c in data])
                texte_cv = next(c['contenu'] for c in data if c['nom_fichier'] == choix)

        if texte_cv:
            if st.button(traduire_avec_ia("🔍 Lancer le Scan & Scoring", st.session_state.langue)):
                with st.spinner("Analyse..."):
                    prompt = f"Analyse ce CV et donne un score ATS (X/100), les points à améliorer et RECRÉE le contenu optimisé : {texte_cv}"
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                    st.session_state.analyse = res.choices[0].message.content
            if 'analyse' in st.session_state:
                st.markdown(st.session_state.analyse)
                match = re.search(r'(\d+)/100', st.session_state.analyse)
                if match: st.progress(int(match.group(1)) / 100)

    with dossiers[4]: # SOURCING
        st.subheader(traduire_avec_ia("🌐 Prospection Spontanée", st.session_state.langue))
        cat = st.selectbox(traduire_avec_ia("Domaine", st.session_state.langue), ["Restauration", "Hôtellerie", "Santé", "Informatique"])
        ville = st.text_input(traduire_avec_ia("Ville", st.session_state.langue))
        if st.button(traduire_avec_ia("🔍 Rechercher 20 contacts", st.session_state.langue)):
            res = client.chat.completions.create(messages=[{"role": "user", "content": f"20 emails {cat} à {ville}"}], model="llama-3.3-70b-versatile")
            st.session_state.emails = res.choices[0].message.content
            st.rerun()
        if 'emails' in st.session_state:
            st.write(st.session_state.emails)
            up = st.file_uploader(traduire_avec_ia("Uploader CV", st.session_state.langue), type=["pdf"])
            if st.button(traduire_avec_ia("🚀 Valider et Envoyer", st.session_state.langue)) and up:
                resend.Emails.send({"from": "onboarding@resend.dev", "to": "test@example.com", "subject": "Candidature", "text": "...", "attachments": [{"filename": "CV.pdf", "content": list(up.getvalue())}]})
                st.success("✅ Envoyé !")

with tab_employeur:
    st.header(traduire_avec_ia("Interface Employeur", st.session_state.langue))
