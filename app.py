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

# --- FONCTIONS ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis ce texte en {langue_cible}. Renvoie uniquement le texte traduit : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

def creer_pdf_cv_pro(texte_ia, nom_fichier, style):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Mon CV Optimisé", ln=True, align='C')
    pdf.multi_cell(0, 7, txt=texte_ia)
    pdf.output(nom_fichier)

def archiver_entretien(candidat_id, statut, lien_jitsi, feedback=""):
    supabase.table("archives_entretiens").insert({
        "candidat_id": candidat_id, "statut": statut, "lien_jitsi": lien_jitsi,
        "feedback": feedback, "date_archivage": str(datetime.datetime.now()),
        "email": st.session_state.user_email
    }).execute()

def generer_lien_magique(candidat_id):
    return f"https://zipngo.app/login?token=zipngo_{candidat_id}_{datetime.datetime.now().strftime('%Y%m%d')}"

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.session_state.langue = st.selectbox("🌐 Langue", LANGUES_DISPONIBLES, index=0)

st.markdown("### 🚀 Bienvenue sur zipngo\nL'application intelligente pour votre trajectoire professionnelle.")

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

# --- ONGLET CANDIDAT COMPLET ---
with tab_candidat:
    st.markdown("### 📘 Mode d'emploi Candidat")
    st.info("Utilisez nos outils pour optimiser votre CV, sourcer des entreprises et simuler vos entretiens.")
    
    is_remote_candidat = st.checkbox("Intéressé par le 100% Remote")
    langues_parlees = st.multiselect("Langues parlées", LANGUES_DISPONIBLES)
    
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[2]: # Relooking
        st.subheader("✨ Relooking CV")
        metier_vise = st.text_input("Poste visé")
        uploaded_file = st.file_uploader("Charger votre CV", type="pdf")
        if uploaded_file and st.button("🚀 Lancer l'optimisation IA"):
            st.success("CV analysé et prêt pour le design.")
    with dossiers[3]: # Sourcing
        st.subheader("🌐 Prospection Spontanée")
        contenu = "Madame, Monsieur, je vous propose ma candidature."
        if st.button("🔍 Générer campagne"):
            st.session_state.emails = ["contact@test.com"]
        if 'emails' in st.session_state:
            st.markdown(f'<a href="mailto:{st.session_state.emails[0]}" style="padding:10px; background:#4169E1; color:white; border-radius:5px; text-decoration:none;">📤 Envoyer (Levée d\'anonymat)</a>', unsafe_allow_html=True)

# --- ONGLET EMPLOYEUR COMPLET ---
with tab_employeur:
    st.header("💼 Interface Recrutement")
    tiroirs = st.tabs(["🔥 Matchs", "📂 Vivier", "👤 Profils", "📅 Entretiens", "🗄️ Archives"])
    
    with st.expander("📝 Nouvelle Offre & Dispatch", expanded=True):
        metier = st.text_input("Intitulé du poste")
        emails_agences = st.text_area("Emails Agences (séparés par virgule)")
        
        is_remote_offre = st.checkbox("Mode 100% Remote")
        if is_remote_offre:
            langue_requise = st.selectbox("Langue requise", LANGUES_DISPONIBLES)
            localisation = "Remote"
        else:
            localisation = st.text_input("Ville / Localisation")
            langue_requise = "Français"
        
        if st.button("✨ Diffuser l'offre"):
            lien = generer_lien_magique(metier)
            mailto = f"mailto:{emails_agences.replace(',', ';')}?subject=Offre {metier}&body=Consultez le profil ici : {lien}"
            st.markdown(f'<a href="{mailto}" style="padding:15px; background:#28a745; color:white; border-radius:5px; text-decoration:none;">📤 DISPATCHER AUX AGENCES</a>', unsafe_allow_html=True)
            
        st.write("### 📢 Multi-Diffusion Sociale")
        if st.button("Générer contenu publication"):
            message = f"🚀 Nous recrutons un(e) {metier} à {localisation}. Postulez ici : {lien}"
            st.text_area("Copiez ce contenu :", value=message)
            st.markdown("[🔗 LinkedIn](https://www.linkedin.com) | [🔗 Apec](https://recrutement.apec.fr) | [🔗 Indeed](https://employers.indeed.com)")

    with tiroirs[3]: # Planning Entretiens
        st.subheader("📅 Entretiens & Planning")
        entretiens = supabase.table("archives_entretiens").select("*").eq("email", st.session_state.user_email).execute()
        if entretiens.data:
            for ent in entretiens.data:
                with st.expander(f"Candidat : {ent['candidat_id']} | Statut : {ent['statut']}"):
                    st.write(f"**Lien vidéo :** [🎥 Rejoindre l'entretien]({ent['lien_jitsi']})")
                    nouveau_feedback = st.text_area(f"Feedback pour {ent['candidat_id']}", value=ent.get('feedback', ''), key=f"feed_{ent['candidat_id']}")
                    if st.button("Enregistrer feedback", key=f"btn_{ent['candidat_id']}"):
                        supabase.table("archives_entretiens").update({"feedback": nouveau_feedback}).eq("candidat_id", ent['candidat_id']).execute()
                        st.success("Feedback mis à jour !")
