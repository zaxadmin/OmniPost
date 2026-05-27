import streamlit as st
import datetime
import re
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader
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

# 1. SÉLECTEUR DE LANGUE
langues = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"]
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue / Select your language", langues, index=0)

# 2. VOTRE SUCCÈS...
st.markdown("<h4 style='color: #4169E1; margin: 20px 0;'>Votre succès professionnel, propulsé par la précision.</h4>", unsafe_allow_html=True)

# 3. BIENVENUE...
st.markdown("""
<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4169E1; margin-bottom: 20px;'>
    <h4 style='margin-top:0;'>Bienvenue sur zipngo</h4>
    L'écosystème intelligent dédié à votre dynamique professionnelle. Que vous soyez en quête de nouvelles opportunités ou en phase de gestion de talents, 
    zipngo agit comme un facilitateur technologique.
</div>
""", unsafe_allow_html=True)

# 4. LIRE LES CGV
with st.expander("📜 Lire les CGV"): afficher_cgv()

# 5. ACCEPTER LES CGV
st.checkbox("J'accepte les CGV", key="accept_cgv")

# 6. ACCUEIL/CANDIDAT/EMPLOYEUR
tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.write("Bienvenue dans votre espace d'accueil.")
    st.markdown("<div style='text-align: center; margin-top: 50px;'>© 2026 zipngo.zaxx.app | <strong>Créatrice : Liliane RAKOTOBE</strong></div>", unsafe_allow_html=True)

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[4]:
        st.subheader("🌐 Prospection Spontanée")
        # Logique de Quota (Simulation)
        is_premium = True # Remplacer par votre logique de vérification réelle
        
        categorie = st.selectbox("Domaine d'activité", ["Restauration", "Hôtellerie", "Commerce", "Santé", "BTP", "Logistique", "Informatique"])
        ville = st.text_input("Ville")
        
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            with st.spinner("Recherche intelligente..."):
                # Récupérer les emails déjà contactés pour les exclure
                exclus = [c['email'] for c in supabase.table("sourcing").select("email").execute().data]
                prompt = f"Donne-moi 20 emails officiels pour {categorie} à {ville}. Exclus strictement ceux-ci : {', '.join(exclus)}. Liste uniquement, séparée par des virgules."
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.emails_trouves = res.choices[0].message.content
        
        if 'emails_trouves' in st.session_state:
            st.write("Emails détectés :", st.session_state.emails_trouves)
            emails_list = [e.strip() for e in st.session_state.emails_trouves.split(',')]
            
            msg = st.text_area("Message", value="Madame, Monsieur, je souhaite rejoindre votre équipe...", height=200)
            
            source_cv = st.radio("Source du CV", ["Choisir parmi mes CVs", "Uploader CV"])
            pdf_content = None
            
            if source_cv == "Choisir parmi mes CVs":
                cv_f = st.selectbox("Mes CVs", [c['nom_fichier'] for c in supabase.table("cvs").select("nom_fichier").execute().data])
            else:
                uploaded = st.file_uploader("Uploader CV", type=["pdf"])
                if uploaded: pdf_content = uploaded.getvalue()

            if st.button("🚀 Valider et Envoyer"):
                try:
                    resend.Emails.send({
                        "from": "contact@zaxx.app", 
                        "to": emails_list[0], 
                        "bcc": emails_list[1:20], 
                        "subject": "Candidature spontanée", 
                        "text": msg, 
                        "attachments": [{"filename": "CV.pdf", "content": list(pdf_content) if pdf_content else []}]
                    })
                    for e in emails_list: 
                        supabase.table("sourcing").insert({"email": e, "date": str(datetime.date.today())}).execute()
                    st.success("✅ Candidatures envoyées !")
                except Exception as e: st.error(f"Erreur : {e}")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
