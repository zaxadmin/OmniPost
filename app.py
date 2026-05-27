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
    st.markdown("### 📜 CGV (Conditions Générales de Vente)\n1. Accès Candidat 6€/3mois | Recruteur 39€/mois.\n2. Limites Gratuit : 1 CV/mois, 1 campagne/mois.\n3. Premium : 3 CVs/semaine, 20 mails/jour.")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#333333; font-size: 14px; margin-top: 0px;'>.zaxx.app</p>", unsafe_allow_html=True)

# --- TEXTE DE PRÉSENTATION ---
st.markdown("<h4 style='color: #4169E1; margin: 20px 0;'>L'intelligence artificielle au service de votre trajectoire professionnelle.</h4>", unsafe_allow_html=True)
st.markdown("""
<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4169E1; margin-bottom: 20px;'>
    <h4 style='margin-top:0;'>Bienvenue sur zipngo</h4>
    Optimisez vos démarches et facilitez vos interactions professionnelles grâce à notre écosystème intelligent, conçu pour accompagner efficacement chaque étape de vos projets de carrière.
</div>
""", unsafe_allow_html=True)

langues = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", "한국어 (Coreen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"]
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue", langues, index=0)

with st.expander("📜 Lire les CGV"): afficher_cgv()
st.checkbox("J'accepte les CGV", key="accept_cgv")

# --- ONGLETS ---
tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.write("Bienvenue dans votre espace d'accueil.")

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[0]:
        st.subheader("📜 Historique des envois")
        try:
            response = supabase.table("sourcing").select("email, date").order("date", desc=True).execute()
            if response.data: st.table(pd.DataFrame(response.data))
        except Exception as e: st.error(f"Erreur : {e}")

    with dossiers[3]: # RELOOKING ATS & SCORING
        st.subheader("✨ Relooking & Scoring ATS")
        source = st.radio("Source", ["Uploader depuis mon ordinateur", "Sélectionner parmi mes CVs enregistrés"])
        
        texte_cv = ""
        if source == "Uploader depuis mon ordinateur":
            up = st.file_uploader("Upload", type=["pdf"])
            if up: texte_cv = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
        else:
            data = supabase.table("cvs").select("nom_fichier, contenu").execute().data
            if data:
                choix = st.selectbox("Mes CVs", [c['nom_fichier'] for c in data])
                texte_cv = next(c['contenu'] for c in data if c['nom_fichier'] == choix)

        if texte_cv:
            if st.button("🔍 Lancer le Scan & Scoring"):
                with st.spinner("Analyse approfondie..."):
                    prompt = f"Analyse ce CV. 1. Score ATS (X/100). 2. Points à améliorer. 3. RECRÉE le contenu du CV avec ces améliorations pour un score de 100/100. CV : {texte_cv}"
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                    st.session_state.analyse = res.choices[0].message.content
            
            if 'analyse' in st.session_state:
                st.markdown(st.session_state.analyse)
                match = re.search(r'(\d+)/100', st.session_state.analyse)
                if match: st.progress(int(match.group(1)) / 100)
                
                if st.button("💾 Sauvegarder la version optimisée"):
                    supabase.table("cvs").insert({"nom_fichier": f"ATS_Optimise_{datetime.date.today()}", "contenu": st.session_state.analyse}).execute()
                    st.success("✅ Version optimisée sauvegardée !")

    with dossiers[4]: # SOURCING
        st.subheader("🌐 Prospection Spontanée")
        categorie = st.selectbox("Domaine", ["Restauration", "Hôtellerie", "Commerce", "Santé", "BTP", "Logistique", "Informatique"])
        ville = st.text_input("Ville")
        
        if st.button("🔍 Rechercher 20 contacts"):
            prompt = f"Donne 20 emails officiels pour {categorie} à {ville}. Liste seule séparée par virgules."
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
            st.session_state.emails_trouves = res.choices[0].message.content
            st.rerun()
            
        if 'emails_trouves' in st.session_state:
            st.write("Emails :", st.session_state.emails_trouves)
            msg = st.text_area("Message", value="""Madame, Monsieur, 

Intégrer votre équipe représente pour moi l'opportunité de mettre mon dynamisme et mon savoir-faire au service de vos objectifs. Je suis convaincu(e) que mon profil pourrait répondre à vos besoins actuels ou futurs.

Vous trouverez ci-joint mon curriculum vitae détaillant mon parcours. Je serais ravi(e) de vous rencontrer lors d'un entretien afin de vous exposer plus en détail mes motivations.

Dans cette attente, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.""", height=250)
            
            uploaded = st.file_uploader("Uploader CV pour envoi", type=["pdf"], key="sourcing_cv")
            if st.button("🚀 Valider et Envoyer"):
                if uploaded:
                    emails = st.session_state.emails_trouves.split(',')
                    resend.Emails.send({"from": "contact@zaxx.app", "to": emails[0], "bcc": emails[1:20], "subject": "Candidature", "text": msg, "attachments": [{"filename": "CV.pdf", "content": list(uploaded.getvalue())}]})
                    for e in emails: supabase.table("sourcing").insert({"email": e.strip(), "date": str(datetime.date.today())}).execute()
                    st.success("✅ Envoyé !")
                    del st.session_state.emails_trouves
                    st.rerun()

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
