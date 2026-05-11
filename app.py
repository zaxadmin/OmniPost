import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
from datetime import datetime, timedelta

# --- 1. CONFIGURATION IA SÉCURISÉE ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Configuration IA manquante dans les Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS (ZAXX BRAND) ---
st.markdown("""
<style>
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 18px; font-weight: 800; margin-top: -15px; text-transform: uppercase; }
    .pay-btn > div > button {
        background-color: #002147 !important; color: #00E5FF !important;
        border: 2px solid #00E5FF !important; font-size: 20px !important;
        height: 60px !important; width: 100%; border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,229,255,0.2);
    }
    .stButton>button { border-radius: 10px !important; font-weight: bold; }
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        background-color: transparent !important; color: #999 !important; border: none !important; font-size: 11px !important; padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS TECHNIQUES ---
def extraire_texte(file):
    with pdfplumber.open(file) as pdf:
        return "".join([page.extract_text() for page in pdf.pages])

def export_pdf(texte):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CV OPTIMISE - ZIPNGO ZAXX", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    txt_clean = texte.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt_clean)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION DES VARIABLES ---
LANGUES = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'validite' not in st.session_state: st.session_state.validite = None
if 'footer_view' not in st.session_state: st.session_state.footer_view = None

# --- 6. HEADER ---
col_l, _ = st.columns([1, 4])
with col_l: st.selectbox("🌐", LANGUES, label_visibility="collapsed")

# --- 7. AUTHENTIFICATION ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    with t1:
        e = st.text_input("Email")
        if st.button("Se connecter 👍"):
            st.session_state.user, st.session_state.role = e, "Candidat"
            st.rerun()
        if st.button("Mot de passe oublié ?"): st.info("Lien envoyé à votre email.")
    with t2:
        ne = st.text_input("Email", key="reg")
        nr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("S'inscrire 🚀"):
            st.session_state.user, st.session_state.role = ne, nr
            st.rerun()

# --- 8. DASHBOARD & LOGIQUE DE VALIDITÉ ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user}**")
        if st.button("Déconnexion"): st.session_state.clear(); st.rerun()

    # Calcul de la validité
    if st.session_state.validite is None:
        # Écran d'activation initiale
        st.subheader("🚀 Activez votre espace Zipngo-Zaxx")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Option Essai")
            duree = "1 jour" if st.session_state.role == "Candidat" else "7 jours"
            if st.button(f"🎁 ESSAI GRATUIT ({duree})"):
                st.session_state.validite = datetime.now() + timedelta(days=(1 if st.session_state.role == "Candidat" else 7))
                st.rerun()
        with c2:
            st.markdown("### Option Production")
            prix = "3 €" if st.session_state.role == "Candidat" else "49 €"
            st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
            if st.button(f"💎 PASS 90 JOURS — {prix}"):
                st.session_state.validite = datetime.now() + timedelta(days=90)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif datetime.now() > st.session_state.validite:
        # Écran de réactivation après expiration
        st.error("⌛ Votre Pass a expiré. Votre profil est actuellement en veille.")
        prix = "3 €" if st.session_state.role == "Candidat" else "49 €"
        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button(f"🚀 RÉACTIVER POUR 90 JOURS — {prix}"):
            st.session_state.validite = datetime.now() + timedelta(days=90)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Interface Active
        jours_restants = (st.session_state.validite - datetime.now()).days
        st.success(f"✅ Pass Actif : Il vous reste {jours_restants} jours d'accès.")
        
        if st.session_state.role == "Candidat":
            tabs = st.tabs(["🎥 Pitch Vidéo", "🤖 Outils IA", "📢 Diffusion"])
            with tabs[0]:
                st.camera_input("Enregistrez votre Pitch (30s)")
                st.button("Publier ma vidéo")
            with tabs[1]:
                f = st.file_uploader("CV (PDF)", type="pdf")
                if f:
                    t = extraire_texte(f)
                    col1, col2 = st.columns(2)
                    if col1.button("🔍 Scan ATS"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Analyse ATS: {t}"}], model="llama3-8b-8192")
                        st.write(res.choices[0].message.content)
                    if col2.button("✨ Relooking CV"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Optimise: {t}"}], model="llama3-8b-8192")
                        opt = res.choices[0].message.content
                        st.download_button("📥 Télécharger PDF", data=export_pdf(opt), file_name="CV_Zaxx.pdf")
            with tabs[2]:
                st.multiselect("Diffuser vers :", ["LinkedIn", "Indeed", "HelloWork"])
                st.button("Lancer Multidiffusion 🚀")
        else:
            st.subheader("Vidéothèque Recruteur")
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")
            st.button("Contacter le candidat")

# --- 9. FOOTER LÉGAL ---
st.divider()
if st.session_state.footer_view == "mentions":
    st.info("⚖️ **MENTIONS LÉGALES** : Responsable Liliane RAKOTOBE. Contact : creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.")
elif st.session_state.footer_view == "cgv":
    st.info("📜 **CGV** : Pass 90j (49€ Recruteur / 3€ Candidat). Paiement immédiat sans remboursement. Mise en veille automatique du profil après 3 mois. Possibilité de réactivation illimitée.")
elif st.session_state.footer_view == "rgpd":
    st.info("🔒 **RGPD** : Données et vidéos sécurisées. Traitement par Intelligence Artificielle confidentiel. Suppression de compte sur simple demande.")

f1, f2, f3, f4 = st.columns([1,1,1,0.5])
with f1: 
    if st.button("Mentions Légales"): st.session_state.footer_view = "mentions"; st.rerun()
with f2: 
    if st.button("CGV & Pass"): st.session_state.footer_view = "cgv"; st.rerun()
with f3: 
    if st.button("RGPD"): st.session_state.footer_view = "rgpd"; st.rerun()
with f4:
    if st.session_state.footer_view:
        if st.button("✖️"): st.session_state.footer_view = None; st.rerun()

st.markdown('<p style="text-align:center; font-size:10px; color:#ccc;">© 2026 Zipngo-Zaxx | Tous droits réservés</p>', unsafe_allow_html=True)
