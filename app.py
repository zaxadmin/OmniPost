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
SALON_FIXE = "https://meet.jit.si/zipngo-entretien-privé"

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
if 'emails_trouves' not in st.session_state: st.session_state.emails_trouves = ""

tab_home, tab_candidat, tab_employeur, tab_cgv = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "📜 CGV"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Le texte de bienvenue et présentation en premier
    st.markdown("""
    ### Bienvenue sur **zipngo**
    Nous transformons la complexité du marché de l'emploi en opportunités concrètes. 
    Que vous cherchiez à décrocher le poste de vos rêves ou à bâtir une équipe d'exception, 
    nous vous offrons les outils pour gagner en efficacité et en clarté.

    * **Pour les Talents :** Valorisation sur-mesure de votre parcours et ciblage direct des décideurs.
    * **Pour les Recruteurs :** Gestion sereine, tri intelligent des profils et rapidité d'exécution.
    """)
    
    st.markdown("---")
    
    # Les blocs de connexion tout en dessous
    col_conn1, col_conn2 = st.columns(2)
    with col_conn1:
        st.subheader("🚀 Espace Candidat")
        email_cand = st.text_input("Email Candidat", key="cand_email")
        if st.button("Connexion Candidat"):
            supabase.auth.sign_in_with_otp({"email": email_cand})
            st.success("Lien envoyé par email.")
            
    with col_conn2:
        st.subheader("💼 Espace Recruteur")
        email_rec = st.text_input("Email Recruteur", key="rec_email")
        if st.button("Connexion Recruteur"):
            supabase.auth.sign_in_with_otp({"email": email_rec})
            st.success("Lien envoyé par email.")

    st.markdown("---")
    st.markdown("### Bienvenue sur **zipngo**")
    st.write("Nous transformons la complexité du marché de l'emploi en opportunités concrètes.")

with tab_candidat:
    st.header("Mon Espace Candidat")
    try:
        response = supabase.table("entretiens").select("*").eq("statut", "en_attente").execute()
        if hasattr(response, 'data') and response.data:
            st.sidebar.error(f"🔔 {len(response.data)} entretien(s) en attente !")
    except Exception:
        pass
    dossiers = st.tabs(["📂 Mes Candidatures", "📅 Mes Entretiens", "📄 Mes CVs", "✨ Relooking IA", "🌐 Sourcing", "🚀 Campagne"])
    with dossiers[2]: up = st.file_uploader("Upload mon CV", type=["pdf"])
    with dossiers[3]:
        poste = st.text_input("Poste visé")
        style = st.selectbox("Style :", ["Classique", "Moderne", "Créatif"])
        if up and poste and st.button("Optimiser"):
            reader = PdfReader(up)
            texte = "".join([p.extract_text() for p in reader.pages])
            res = client.chat.completions.create(messages=[{"role": "user", "content": f"Optimise ce CV pour {poste}: {texte}"}], model="llama-3.3-70b-versatile")
            creer_pdf_cv_pro(res.choices[0].message.content, "cv_opt.pdf", style)
            with open("cv_opt.pdf", "rb") as f: st.download_button("📥 Télécharger", f, "cv_opt.pdf")
    with dossiers[4]:
        secteur = st.text_input("Secteur")
        if st.button("Identifier"):
            res = client.chat.completions.create(messages=[{"role": "user", "content": f"Donne 20 emails RH en {secteur}. Liste séparée par virgules."}], model="llama-3.3-70b-versatile")
            st.session_state.emails_trouves = res.choices[0].message.content
            st.info("✅ Étape suivante : Allez dans l'onglet '🚀 Campagne'.")
    with dossiers[5]:
        dest = st.text_input("Expéditeur")
        bcc = st.text_area("Emails cibles", value=st.session_state.emails_trouves)
        cv = st.file_uploader("CV pour envoi", type=["pdf"])
        if st.button("Lancer envoi"):
            if envoyer_email_avec_cv(dest, bcc.split(","), "Candidature", "Voici mon CV.", cv): st.success("Campagne lancée !")

with tab_employeur:
    st.header("Interface Employeur")
    with st.expander("ℹ️ Pourquoi connecter votre boîte mail ?"):
        st.write("Votre boîte mail devient un tableau de bord intelligent pour centraliser et organiser vos candidatures.")
    email_a_trier = st.text_input("Email de réception à trier")
    if st.button("🚀 Lancer le Tri Intelligent"): st.write("Analyse en cours...")

with tab_cgv:
    st.markdown("## 📜 Conditions Générales de Vente")
    st.markdown("1. Objet : Services d'optimisation de carrière. 2. Tarifs : Candidat 6€/3mois | Recruteur 39€/mois. 3. Responsabilité : Outil technologique sans garantie de résultat. 4. Propriété : Propriété exclusive de zaxx.app.")
