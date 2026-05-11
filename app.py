import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURATION IA SÉCURISÉE ---
try:
    # Récupération de la clé via .streamlit/secrets.toml
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Erreur : GROQ_API_KEY introuvable dans les Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS AVANCÉ (MARINE, CYAN & FOND DYNAMIQUE) ---
st.markdown("""
<style>
    /* Fond dégradé moderne */
    .stApp {
        background: linear-gradient(160deg, #001529 0%, #002147 50%, #0a3d62 100%);
        color: white;
    }

    /* Conteneurs blancs pour le contenu pour assurer la lisibilité */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
    }

    /* Style du Logo et Titres */
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #00E5FF; text-align: center; margin: 0; letter-spacing: -2px; }
    .power-title { text-align: center; color: #FFFFFF; font-size: 16px; font-weight: 400; margin-top: -15px; text-transform: uppercase; letter-spacing: 3px; }
    
    /* Boutons de paiement Premium (Marine & Cyan) */
    .pay-btn > div > button {
        background-color: #00E5FF !important; /* Cyan */
        color: #002147 !important; /* Marine */
        border: none !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 70px !important;
        width: 100%;
        border-radius: 15px !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
        transition: 0.4s;
    }
    .pay-btn > div > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 35px rgba(0, 229, 255, 0.6);
        background-color: #FFFFFF !important;
    }
    
    /* Boutons Standards */
    .stButton>button {
        border-radius: 10px !important;
        background-color: transparent !important;
        color: #00E5FF !important;
        border: 1px solid #00E5FF !important;
    }
    .stButton>button:hover {
        background-color: #00E5FF !important;
        color: #002147 !important;
    }

    /* Sidebar et Inputs */
    .css-1d391kg { background-color: #001529 !important; }
    label { color: #00E5FF !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS TECHNIQUES ---
def extraire_texte_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])
    except Exception as e: return f"Erreur : {e}"

def generer_pdf_cv(texte_optimise):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CV OPTIMISE - ZIPNGO ZAXX", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    texte_propre = texte_optimise.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, texte_propre)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION ---
LISTE_LANGUES = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'validite' not in st.session_state: st.session_state.validite = None
if 'footer_view' not in st.session_state: st.session_state.footer_view = None

# --- 6. HEADER (LANGUES) ---
col_lang, _ = st.columns([1, 4])
with col_lang:
    st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

# --- 7. LOGO ET AUTHENTIFICATION ---
if not st.session_state.user:
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
    with col_logo_2:
        if os.path.exists("_20260511_163213.JPG"):
            st.image("_20260511_163213.JPG", use_column_width=True)
        else:
            st.markdown('<p class="main-logo-text">zipngo👍</p>', unsafe_allow_html=True)
        st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    with t1:
        e = st.text_input("Email")
        st.text_input("Mot de passe", type="password")
        if st.button("Se connecter 👍"):
            st.session_state.user, st.session_state.role = e, "Candidat"
            st.rerun()
    with t2:
        ne = st.text_input("Nouvel Email", key="reg")
        nr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("S'inscrire 🚀"):
            st.session_state.user, st.session_state.role = ne, nr
            st.rerun()

# --- 8. DASHBOARD ET LOGIQUE DE VALIDITÉ ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.info(f"Rôle : {st.session_state.role}")
        if st.button("Déconnexion"):
            st.session_state.clear(); st.rerun()

    # --- LOGIQUE D'ACTIVATION ---
    if st.session_state.validite is None:
        st.subheader("🚀 Activez votre espace de production")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🎁 Essai Gratuit")
            duree = "1 jour" if st.session_state.role == "Candidat" else "7 jours"
            if st.button(f"Lancer l'essai ({duree})"):
                j = 1 if st.session_state.role == "Candidat" else 7
                st.session_state.validite = datetime.now() + timedelta(days=j)
                st.rerun()
        with c2:
            st.markdown("#### 💎 Accès Premium")
            prix = "3 €" if st.session_state.role == "Candidat" else "49 €"
            st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
            if st.button(f"ACTIVER LE PASS 90J — {prix}"):
                st.session_state.validite = datetime.now() + timedelta(days=90)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif datetime.now() > st.session_state.validite:
        st.error("⌛ Votre Pass a expiré. Votre profil est en veille.")
        prix_reac = "3 €" if st.session_state.role == "Candidat" else "49 €"
        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button(f"🚀 RÉACTIVER LE PASS — {prix_reac}"):
            st.session_state.validite = datetime.now() + timedelta(days=90)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- INTERFACE ACTIVE ---
        jours = (st.session_state.validite - datetime.now()).days
        st.markdown(f"<h3 style='color:#00E5FF;'>✅ Accès Actif : J-{jours}</h3>", unsafe_allow_html=True)
        
        if st.session_state.role == "Candidat":
            tabs = st.tabs(["🎥 Pitch Vidéo", "🤖 IA Production", "📢 Diffusion"])
            with tabs[0]:
                st.camera_input("Enregistrez votre Pitch 30s")
                st.button("Publier mon profil vidéo")
            with tabs[1]:
                f = st.file_uploader("Charger CV (PDF)", type="pdf")
                if f:
                    txt = extraire_texte_pdf(f)
                    col1, col2 = st.columns(2)
                    if col1.button("🔍 Scan ATS"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Analyse ATS: {txt}"}], model="llama3-8b-8192")
                        st.write(res.choices[0].message.content)
                    if col2.button("✨ Relooking CV"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Optimise: {txt}"}], model="llama3-8b-8192")
                        st.download_button("📥 Télécharger PDF", data=generer_pdf_cv(res.choices[0].message.content), file_name="CV_Zaxx.pdf")
            with tabs[2]:
                st.multiselect("Partager sur :", ["LinkedIn", "Indeed", "HelloWork", "Zaxx Network"])
                st.button("Lancer la multidiffusion 🚀")
        else:
            st.subheader("Vidéothèque Recruteur")
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")
            st.button("Contacter ce candidat")

# --- 9. FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
if st.session_state.footer_view == "mentions":
    st.info("⚖️ **MENTIONS** : Liliane RAKOTOBE. creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.")
elif st.session_state.footer_view == "cgv":
    st.info("📜 **CGV** : Pass 90j (49€ Recruteur / 3€ Candidat). Règlement immédiat sans remboursement. Mise en veille auto après 90 jours.")
elif st.session_state.footer_view == "rgpd":
    st.info("🔒 **RGPD** : Vidéos et données sécurisées. IA confidentielle. Suppression sur simple demande.")

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

st.markdown('<p style="text-align:center; font-size:12px; color:#00E5FF; margin-top:20px;">© 2026 Zipngo-Zaxx | The Power of Choice</p>', unsafe_allow_html=True)
