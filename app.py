import streamlit as st
import datetime
import pandas as pd
import io
import json
import urllib.parse
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

# --- FONCTIONS D'ORIGINE ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

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

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse pour le poste '{metier}'. Retourne uniquement un JSON structuré avec: 'header', 'sidebar', 'main', 'mots_cles_ajoutes'. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("```", ""))

def appliquer_design_geometrique(pdf, data):
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, data['header']['nom'], ln=True)
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, data['header']['titre_poste'], ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, data['main']['titre'], ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, data['main']['corps'])

# --- MOTEUR DE TRI AUTOMATIQUE ---
def trier_candidats_auto(offre_data):
    profils = supabase.table("candidats").select("*").execute().data
    for p in profils:
        prompt = "Compare le CV: {} et l'Offre: {}. Score 0-100. Retourne un JSON strictement comme ceci: {{\"score\": 0}}".format(
            p.get('cv_text', 'Non disponible'), offre_data
        )
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        try:
            score = json.loads(res.choices[0].message.content.replace("```json", "").replace("```", "")).get('score', 0)
            statut = "Matchs" if score >= 50 else "Vivier"
            supabase.table("candidats").update({"statut": statut, "score": score}).eq("id", p['id']).execute()
        except: continue

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

tab_candidat, tab_employeur = st.tabs(["🚀 Espace Candidat", "💼 Espace Recruteur"])

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[2]:
        metier = st.text_input("Poste visé")
        up = st.file_uploader("Upload CV", type=["pdf"])
        if up and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            st.download_button("⬇️ Télécharger CV", data=pdf.output(dest='S').encode('latin-1'), file_name="CV.pdf")

with tab_employeur:
    st.subheader("📢 Création et Dispatch automatique")
    with st.container():
        col1, col2 = st.columns(2)
        titre = col1.text_input("Intitulé du poste")
        ville = col2.text_input("Ville")
        remote = st.checkbox("Télétravail possible")
        skills = st.text_area("Compétences requises")
        
        if st.button("✨ Publier et Dispatcher les profils"):
            offre_full = f"{titre} à {ville}, Remote: {remote}, Skills: {skills}"
            supabase.table("offres").insert({"titre": titre, "details": offre_full}).execute()
            trier_candidats_auto(offre_full)
            st.success("Offre publiée et base de candidats dispatchée !")
            st.rerun()

    tiroirs = st.tabs(["🔥 Matchs", "📂 Vivier", "👤 Profils", "📅 Entretiens", "🗄️ Archives"])
    with tiroirs[0]:
        for c in supabase.table("candidats").select("*").gte("score", 50).execute().data:
            with st.expander(f"{c.get('nom_candidat')} - Score: {c.get('score')}%"):
                if st.button(f"👍 Offrir Entretien", key=f"m_{c['id']}"): st.success("Entretien proposé !")
    with tiroirs[1]:
        for c in supabase.table("candidats").select("*").lt("score", 50).execute().data:
            st.write(f"- {c.get('nom_candidat')} (Score: {c.get('score')}%)")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align:center;'>Créé par <b>Liliane RAKOTOBE</b> | <a href='mailto:creationsites06@gmail.com'>📧</a></div>", unsafe_allow_html=True)
