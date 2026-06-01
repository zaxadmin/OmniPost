import streamlit as st
import datetime, pandas as pd, io, json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTIONS ---
def envoyer_lien_magique(email):
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        st.success(f"Lien magique envoyé à {email}. Vérifiez vos emails.")
    except Exception as e: st.error(f"Erreur : {e}")

def obtenir_contenu_structure(txt_cv, metier):
    # Prompt renforcé pour éviter les erreurs de clés manquantes
    prompt = f"""Analyse ce CV pour le poste '{metier}'. 
    Retourne TOUJOURS un JSON strictement structuré avec ces clés exactes:
    {{"header": {{"nom": "Nom Complet", "titre_poste": "Titre", "contact": "Tel/Email"}}, 
      "sidebar": {{"contenu": "Compétences clés"}}, 
      "main": {{"titre": "Résumé", "corps": "Expériences détaillées"}}, 
      "mots_cles_ajoutes": "liste de mots clés"}}
    CV original: {txt_cv}"""
    
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    # Nettoyage et parsing
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("```", ""))

def appliquer_design_geometrique(pdf, data):
    # Sécurisation avec .get() pour éviter le KeyError si l'IA oublie une clé
    h = data.get('header', {})
    s = data.get('sidebar', {})
    m = data.get('main', {})
    
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, h.get('nom', 'Inconnu'), ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, h.get('contact', 'Non renseigné'))
    
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, s.get('contenu', ''))
    
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, h.get('titre_poste', ''), ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, m.get('titre', ''), ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, m.get('corps', ''))

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

with st.sidebar:
    params = st.query_params
    if "access_token" in params or "type" in params: st.rerun()
    session = supabase.auth.get_session()
    if session: 
        st.success(f"Connecté : {session.user.email}")
    else:
        email_in = st.text_input("Votre email")
        if st.button("Envoyer mon lien"): envoyer_lien_magique(email_in)

tabs = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "🔄 Matching"])

with tabs[1]:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[1]:
        nom = st.text_input("Nom du doc")
        up = st.file_uploader("Upload", type=["pdf", "txt"])
        if st.button("💾 Enregistrer"):
            user = supabase.auth.get_user()
            if user and user.user:
                supabase.table("cvs").insert({"user_id": user.user.id, "nom_fichier": nom, "contenu": str(up.getvalue())}).execute()
                st.success("CV enregistré !")
            else: st.error("Connexion requise.")
    with dossiers[2]:
        metier = st.text_area("Intitulé du poste...")
        up_cv = st.file_uploader("Upload CV", type=["pdf"])
        if up_cv and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            st.download_button("⬇️ Télécharger CV", data=pdf.output(dest='S').encode('latin-1'), file_name="CV_Optimise.pdf")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center;'><a href='mailto:creationsites06@gmail.com'>📧</a></div>", unsafe_allow_html=True)
