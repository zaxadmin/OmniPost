import streamlit as st
import imaplib
import email
import requests
import base64
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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

def envoyer_email_avec_cv(dest, bcc, sujet, contenu, cv_file):
    cv_b64 = base64.b64encode(cv_file.getvalue()).decode()
    payload = {
        "from": "contact@zipngo.zaxx.app", "to": dest, "bcc": bcc, "subject": sujet,
        "html": contenu, "attachments": [{"filename": cv_file.name, "content": cv_b64}]
    }
    response = requests.post("https://api.resend.com/emails", 
        headers={"Authorization": f"Bearer {st.secrets['RESEND_API_KEY']}"}, json=payload)
    return response.status_code == 200

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app</h1>", unsafe_allow_html=True)
session = supabase.auth.get_session()

tab_home, tab_candidat, tab_employeur, tab_cgv = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "📜 CGV"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    ### Bienvenue sur **zipngo**
    Nous transformons la complexité du marché de l'emploi en opportunités concrètes. Que vous cherchiez à décrocher le poste de vos rêves ou à bâtir une équipe d'exception, nous vous offrons les outils pour gagner en efficacité et en clarté.

    * **Pour les Talents :** Valorisation sur-mesure de votre parcours et ciblage direct des décideurs.
    * **Pour les Recruteurs :** Gestion sereine, tri intelligent des profils et rapidité d'exécution.
    """)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Espace Candidat")
        email_cand = st.text_input("Email Candidat", key="cand_email")
        if st.button("Connexion Candidat"):
            supabase.auth.sign_in_with_otp({"email": email_cand})
            st.success("Lien magique envoyé par email.")
    with col2:
        st.subheader("💼 Espace Recruteur")
        email_rec = st.text_input("Email Recruteur", key="rec_email")
        if st.button("Connexion Recruteur"):
            supabase.auth.sign_in_with_otp({"email": email_rec})
            st.success("Lien magique envoyé par email.")

with tab_candidat:
    if not session:
        st.warning("⚠️ Veuillez vous connecter depuis l'accueil pour accéder à votre espace.")
    else:
        st.header("Mon Espace Candidat")
        # (Ton code de dossiers candidat reste ici)
        st.write("Bienvenue dans votre espace sécurisé.")

with tab_employeur:
    if not session:
        st.warning("⚠️ Veuillez vous connecter depuis l'accueil pour accéder à votre espace.")
    else:
        st.header("Interface Employeur")
        # (Ton code employeur reste ici)
        st.write("Outils de gestion activés.")

with tab_cgv:
    st.markdown("## 📜 Conditions Générales de Vente")
    st.markdown("1. Objet : Services d'optimisation. 2. Tarifs : Candidat 6€/3mois | Recruteur 39€/mois. 3. Propriété exclusive de zaxx.app.")
