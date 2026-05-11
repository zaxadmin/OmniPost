import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURATION IA SÉCURISÉE ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Configuration IA manquante dans les Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS AVANCÉ (MARINE, CYAN & TEXTES BLANCS) ---
st.markdown("""
<style>
    /* Fond dégradé moderne */
    .stApp {
        background: linear-gradient(160deg, #001529 0%, #002147 50%, #0a3d62 100%);
        color: white !important;
    }

    /* Forcer tout le texte en blanc par défaut */
    .stApp, p, span, label, div {
        color: white !important;
    }

    /* Conteneurs transparents avec bordure Cyan */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
    }

    /* Style du Logo et Titres */
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #00E5FF !important; text-align: center; margin: 0; letter-spacing: -2px; }
    .power-title { text-align: center; color: #FFFFFF !important; font-size: 16px; font-weight: 400; margin-top: -15px; text-transform: uppercase; letter-spacing: 3px; }
    
    /* Boutons de paiement Premium (Cyan & Marine) */
    .pay-btn > div > button {
        background-color: #00E5FF !important; 
        color: #002147 !important; 
        border: none !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 70px !important;
        width: 100%;
        border-radius: 15px !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
    }
    
    /* Boutons Standards (Bordure Cyan, Texte Blanc) */
    .stButton>button {
        border-radius: 10px !important;
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #00E5FF !important;
    }
    .stButton>button:hover {
        background-color: #00E5FF !important;
        color: #002147 !important;
    }

    /* Alertes (Remplacer le fond rouge/jaune par du sombre/cyan pour le texte blanc) */
    .stAlert {
        background-color: rgba(0, 33, 71, 0.8) !important;
        border: 1px solid #00E5FF !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
    }
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
        e = st.text_input("Email", key="login_val")
        st.text_input("Mot de passe", type="password")
        if st.button("Se connecter 👍"):
            st.session_state.user, st.session_state.role = e, "Candidat"
            st.rerun()
    with t2:
        ne = st.text_input("Nouvel Email", key="reg_val")
        nr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("S'inscrire 🚀"):
            st.session_state.user, st.session_state.role = ne, nr
            st.rerun()

# --- 8. DASHBOARD ET LOGIQUE DE VALIDITÉ ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user}")
        st.write(f"Accès : {st.session_state.role}")
        if st.button("Déconnexion"):
            st.session_state.clear(); st.rerun()

    if st.session_state.validite is None:
        st.subheader("🚀 Activez votre espace")
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
        st.markdown("<p style='color:white; background:rgba(255,0,0,0.2); padding:10px; border-radius:5px;'>⌛ Votre Pass a expiré. Votre profil est en veille.</p>", unsafe_allow_html=True)
        prix_reac = "3 €" if st.session_state.role == "Candidat" else "49 €"
        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button(f"🚀 RÉACTIVER LE PASS — {prix_reac}"):
            st.session_state.validite = datetime.now() + timedelta(days=90)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
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
                    c1, c2 = st.columns(2)
                    if c1.button("🔍 Scan ATS"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Analyse ATS: {txt}"}], model="llama3-8b-8192")
                        st.write(res.choices[0].message.content)
                    if c2.button("✨ Relooking CV"):
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
    st.markdown("<div style='color:white;'>⚖️ <b>MENTIONS</b> : Liliane RAKOTOBE. creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.</div>", unsafe_allow_html=True)
elif st.session_state.footer_view == "cgv":
    st.markdown("<div style='color:white;'>📜 <b>CGV</b> : Pass 90j (49€ Recruteur / 3€ Candidat). Règlement immédiat sans remboursement.</div>", unsafe_allow_html=True)
elif st.session_state.footer_view == "rgpd":
    st.markdown("<div style='color:white;'>🔒 <b>RGPD</b> : Vidéos et données sécurisées. IA confidentielle.</div>", unsafe_allow_html=True)

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
