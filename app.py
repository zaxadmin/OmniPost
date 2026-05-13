import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
from datetime import datetime, timedelta
from supabase import create_client, Client
import hashlib
import os

# --- 1. CONFIGURATION IA & BASE DE DONNÉES ---
try:
    # IA Groq
    GROQ_KEY = st.secrets.get("GROQ_API_KEY")
    client_ia = Groq(api_key=GROQ_KEY)
    # Supabase
    URL = st.secrets.get("SUPABASE_URL")
    KEY = st.secrets.get("SUPABASE_KEY")
    api_conn = create_client(URL, KEY)
except Exception:
    st.error("⚠️ Configuration Secrets manquante (Groq ou Supabase).")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS PREMIUM (FUSION DES DEUX VERSIONS) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #001529 0%, #002147 50%, #0a3d62 100%);
        color: white !important;
    }
    .stApp, p, span, label, div, h1, h2, h3, .stMarkdown { color: white !important; }
    
    /* Style des Tiroirs (Expanders) */
    [data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
        margin-bottom: 12px;
    }

    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #00E5FF !important; text-align: center; margin: 0; letter-spacing: -2px; }
    .power-title { text-align: center; color: #FFFFFF !important; font-size: 16px; font-weight: 400; margin-top: -15px; text-transform: uppercase; letter-spacing: 3px; }
    
    /* Boutons Flashy Cyan */
    .stButton>button {
        border-radius: 10px !important;
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #00E5FF !important;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #00E5FF !important; color: #002147 !important; }
    
    .pay-btn > div > button {
        background-color: #00E5FF !important; 
        color: #002147 !important; 
        font-size: 20px !important;
        height: 60px !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
    }
    [data-testid="stSidebar"] { background-color: #001529 !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS TECHNIQUES ---
def crypt_str(s):
    return hashlib.sha256(s.strip().lower().encode('utf-8')).hexdigest()

def extraire_texte_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])
    except Exception: return "Erreur de lecture."

def generer_pdf_cv(texte_optimise):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    texte_propre = texte_optimise.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, texte_propre)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION DES DONNÉES ---
LISTE_LANGUES = ["Français", "English", "Malagasy", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Arabe", "Russe", "Japonais", "Hindi", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Grec", "Roumain"]
QUESTIONS_SECURE = ["Nom de mon premier animal ?", "Ma ville de naissance ?", "Nom de ma première école ?", "Marque de ma première voiture ?"]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'auth' not in st.session_state: st.session_state.auth = False
if 'validite' not in st.session_state: st.session_state.validite = None
if 'recovery_mode' not in st.session_state: st.session_state.recovery_mode = False
if 'video_validated' not in st.session_state: st.session_state.video_validated = False
if 'footer_view' not in st.session_state: st.session_state.footer_view = None

# --- 6. LOGIQUE DE RÉCUPÉRATION AUTONOME ---
def recovery_ui():
    st.subheader("🔑 Récupération d'accès autonome")
    email_check = st.text_input("Email de connexion").lower()
    q_check = st.selectbox("Question de sécurité", QUESTIONS_SECURE)
    r_check = st.text_input("Réponse secrète", type="password")
    if st.button("Vérifier mon identité"):
        # Logique Supabase ici
        st.success("Identité confirmée. Définissez votre nouvelle clé.")
        st.text_input("Nouvelle clé", type="password")
        if st.button("Valider"):
            st.session_state.recovery_mode = False; st.rerun()
    if st.button("Retour"): st.session_state.recovery_mode = False; st.rerun()

# --- 7. PORTAIL D'ACCÈS ---
if not st.session_state.auth:
    if st.session_state.recovery_mode:
        recovery_ui()
    else:
        col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
        with col_logo_2:
            if os.path.exists("_20260511_163213.JPG"): st.image("_20260511_163213.JPG", use_column_width=True)
            else: st.markdown('<p class="main-logo-text">zipngo👍</p>', unsafe_allow_html=True)
            st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)

        t1, t2 = st.tabs(["Connexion", "Créer un compte"])
        with t1:
            u = st.text_input("Email").lower()
            p = st.text_input("Clé d'accès", type="password")
            c1, c2 = st.columns(2)
            if c1.button("Accès Recruteur"):
                st.session_state.update({"auth":True, "user":u, "role":"Employeur"}); st.rerun()
            if c2.button("Accès Candidat"):
                st.session_state.update({"auth":True, "user":u, "role":"Candidat"}); st.rerun()
            st.button("🔑 Clé perdue ?", on_click=lambda: st.session_state.update({"recovery_mode":True}))

# --- 8. DASHBOARD ACTIF ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.write(f"Rôle : {st.session_state.role}")
        if st.button("Déconnexion"): st.session_state.clear(); st.rerun()

    # Gestion de la validité (Pass)
    if st.session_state.validite is None:
        st.subheader("🚀 Activation de votre espace")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Démarrer Essai Gratuit"):
                st.session_state.validite = datetime.now() + timedelta(days=1); st.rerun()
        with c2:
            st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
            if st.button("ACTIVER PASS 90J"):
                st.session_state.validite = datetime.now() + timedelta(days=90); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Interface selon le rôle
        if st.session_state.role == "Candidat":
            tabs = st.tabs(["🎥 Pitch Vidéo", "🤖 IA Production", "📢 Diffusion"])
            with tabs[1]:
                f = st.file_uploader("CV PDF", type="pdf")
                if f:
                    txt = extraire_texte_pdf(f)
                    if st.button("✨ Relooking IA"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Optimise ce CV: {txt}"}], model="llama3-8b-8192")
                        st.download_button("📥 Télécharger", data=generer_pdf_cv(res.choices[0].message.content), file_name="CV_Zaxx.pdf")
        else:
            # Interface Employeur
            with st.expander("📂 Tiroir : Dispatcher IA & Flux", expanded=True):
                st.table([{"ID": "CAND-001", "Match": "98%", "Langues": "Fr, En", "Statut": "🔒 Masqué"}])
            with st.expander("📂 Tiroir : Configuration & Emails"):
                st.text_input("Email de connexion", value=st.session_state.user)
                st.text_input("Email de réception CV", value="flux@entreprise.com")
                st.selectbox("Question de sécurité", QUESTIONS_SECURE)
                st.button("💾 Sauvegarder")

# --- 9. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True); st.divider()
f1, f2, f3 = st.columns(3)
with f1: 
    if st.button("Mentions"): st.session_state.footer_view = "mentions"; st.rerun()
with f2: 
    if st.button("CGV"): st.session_state.footer_view = "cgv"; st.rerun()
with f3: 
    if st.button("RGPD"): st.session_state.footer_view = "rgpd"; st.rerun()

st.markdown('<p style="text-align:center; font-size:12px; color:#00E5FF;">© 2026 Zipngo-Zaxx | Système Autonome | Liliane RAKOTOBE</p>', unsafe_allow_html=True)
