import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
import time

# --- CONFIGURATION GROQ ---
# Remplace par ta clé ou utilise st.secrets["GROQ_API_KEY"] sur Streamlit Cloud
GROQ_KEY = "TA_CLE_GROQ_ICI" 
client_ia = Groq(api_key=GROQ_KEY)

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- STYLE CSS ---
st.markdown("""
<style>
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 18px; font-weight: 800; margin-top: -15px; text-transform: uppercase; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; font-weight: bold; height: 45px; width: 100%; }
    .stButton>button:hover { background-color: #F3812B !important; }
</style>
""", unsafe_allow_html=True)

# --- FONCTIONS TECHNIQUES ---
def extraire_texte(file):
    with pdfplumber.open(file) as pdf:
        return "".join([page.extract_text() for page in pdf.pages])

def generer_pdf_simple(texte):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, texte)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- INITIALISATION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'essai_active' not in st.session_state: st.session_state.essai_active = False

# --- PARCOURS UTILISATEUR ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
    with tab2:
        email = st.text_input("Email")
        role = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("S'inscrire 🚀"):
            st.session_state.user = email
            st.session_state.role = role
            st.rerun()
else:
    # --- DASHBOARD APRES CONNEXION ---
    with st.sidebar:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Déconnexion"):
            st.session_state.clear(); st.rerun()

    if not st.session_state.essai_active:
        st.info("🎁 Activez votre essai gratuit pour utiliser l'IA.")
        if st.button("Démarrer l'essai gratuit 🚀"):
            st.session_state.essai_active = True
            st.rerun()
    else:
        # --- PRODUCTION IA (ESPACE CANDIDAT) ---
        if st.session_state.role == "Candidat":
            st.subheader("🛠️ Pack IA Candidat")
            file = st.file_uploader("Chargez votre CV (PDF)", type="pdf")
            
            if file:
                texte_cv = extraire_texte(file)
                st.success("CV chargé avec succès.")
                
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    if st.button("🔍 Scan ATS"):
                        with st.spinner("Analyse..."):
                            prompt = f"Analyse ce CV et donne un score ATS sur 100 et 3 conseils : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                            st.write(res.choices[0].message.content)
                
                with c2:
                    if st.button("✨ Relooking Texte"):
                        with st.spinner("Optimisation..."):
                            prompt = f"Réécris ce CV avec des Power Phrases percutantes : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                            txt_relooke = res.choices[0].message.content
                            st.session_state.cv_relooke = txt_relooke
                            st.write(txt_relooke)
                            st.download_button("📥 Télécharger PDF", data=generer_pdf_simple(txt_relooke), file_name="CV_Zaxx.pdf")

                with c3:
                    if st.button("✍️ Lettre Motivation"):
                        with st.spinner("Rédaction..."):
                            prompt = f"Rédige une lettre de motivation basée sur ce CV : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                            st.text_area("Lettre :", res.choices[0].message.content, height=200)

            st.divider()
            if st.button("💎 Activer Pass 90j — 3 €"):
                st.warning("Lien vers tunnel de paiement...")

        else:
            st.subheader("🔍 Espace Recruteur")
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")
            if st.button("💎 Activer Pass 90j — 49 €"):
                st.write("Redirection paiement...")

# --- FOOTER DISCRET ---
st.divider()
st.markdown('<p style="text-align:center; font-size:10px; color:#999;">© 2026 Zipngo-Zaxx | Mentions Légales | CGV (Pas de remboursement) | Contact : RAKOTOBE Liliane</p>', unsafe_allow_html=True)
