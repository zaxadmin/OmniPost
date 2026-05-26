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

def afficher_cgv():
    st.markdown("""
    ### 📜 Conditions Générales de Vente
    1. **Objet :** Services d'optimisation zipngo/zaxx.app.
    2. **Tarifs :** Candidat 6€/3mois | Recruteur 39€/mois.
    3. **Non-garantie :** Outil d'aide, aucune garantie d'emploi.
    4. **Responsabilité :** Utilisateur seul responsable de ses usages.
    5. **Propriété :** Code et algorithmes propriété de zaxx.app.
    6. **Données :** Collecte minimale, aucune vente à des tiers.
    7. **Juridiction :** Droit français.
    """)

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app</h1>", unsafe_allow_html=True)
if 'emails_trouves' not in st.session_state: st.session_state.emails_trouves = ""

session = supabase.auth.get_session()

# Navigation dynamique : N'affiche les onglets que si connecté
if not session:
    tab_home = st.tabs(["🏠 Accueil"])[0]
else:
    tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    ### Bienvenue sur **zipngo**
    Nous transformons la complexité du marché de l'emploi en opportunités concrètes.
    * **Pour les Talents :** Valorisation sur-mesure et ciblage direct des décideurs.
    * **Pour les Recruteurs :** Gestion sereine, tri intelligent des profils et rapidité.
    """)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 Espace Candidat")
        email_cand = st.text_input("Email Candidat", key="cand_email")
        if st.button("Connexion Candidat"):
            supabase.auth.sign_in_with_otp({"email": email_cand})
            st.success("Lien envoyé par email.")
    with col2:
        st.subheader("💼 Espace Recruteur")
        email_rec = st.text_input("Email Recruteur", key="rec_email")
        if st.button("Connexion Recruteur"):
            supabase.auth.sign_in_with_otp({"email": email_rec})
            st.success("Lien envoyé par email.")

if session:
    with tab_candidat:
        st.header("Mon Espace Candidat")
        # (Ton code dossiers candidat ici)
        with st.expander("📜 Voir les CGV"):
            afficher_cgv()
            
    with tab_employeur:
        st.header("Interface Employeur")
        # (Ton code employeur ici)
        with st.expander("📜 Voir les CGV"):
            afficher_cgv()
