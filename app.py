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
    L'écosystème intelligent dédié à votre dynamique professionnelle.
</div>
""", unsafe_allow_html=True)

# 4. LIRE LES CGV
with st.expander("📜 Lire les CGV"): afficher_cgv()

# 5. ACCEPTER LES CGV
st.checkbox("J'accepte les CGV", key="accept_cgv")

# 6. ONGLETS
tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.write("Bienvenue dans votre espace d'accueil.")

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[4]:
        st.subheader("🌐 Prospection Spontanée")
        categorie = st.selectbox("Domaine d'activité", ["Restauration", "Hôtellerie", "Commerce", "Santé", "BTP", "Logistique", "Informatique"])
        ville = st.text_input("Ville")
        
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            with st.spinner("Recherche..."):
                try:
                    response = supabase.table("sourcing").select("email").execute()
                    exclus = [c['email'] for c in response.data] if response.data else []
                except: exclus = []
                
                prompt = f"Donne 20 emails officiels pour {categorie} à {ville}. Exclus strictement ceux-ci : {', '.join(exclus)}. Liste seule séparée par virgules."
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.emails_trouves = res.choices[0].message.content
                st.rerun()
        
        if 'emails_trouves' in st.session_state:
            st.write("Emails :", st.session_state.emails_trouves)
            emails_list = [e.strip() for e in st.session_state.emails_trouves.split(',')]
            msg = st.text_area("Message", value="Madame, Monsieur, Intégrer votre équipe représente pour moi l'opportunité de mettre mon dynamisme et mon savoir-faire au service de vos objectifs. Je suis convaincu(e) que mon profil pourrait répondre à vos besoins actuels ou futurs.
​Vous trouverez ci-joint mon curriculum vitae détaillant mon parcours. Je serais ravi(e) de vous rencontrer lors d'un entretien afin de vous exposer plus en détail mes motivations.
​Dans cette attente, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.", height=200)
            
            uploaded = st.file_uploader("Uploader CV (PDF)", type=["pdf"])
            
            if st.button("🚀 Valider et Envoyer"):
                try:
                    pdf_content = uploaded.getvalue() if uploaded else None
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
                    st.success("✅ Candidatures envoyées et archivées !")
                    del st.session_state.emails_trouves
                except Exception as e: st.error(f"Erreur : {e}")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
