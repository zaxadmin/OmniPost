import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
import time

# --- 1. CONFIGURATION IA SÉCURISÉE ---
try:
    # Récupération de la clé dans .streamlit/secrets.toml
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Erreur de configuration : Clé IA introuvable dans les Secrets.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS PROFESSIONNEL (ZAXX COLORS) ---
st.markdown("""
<style>
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 18px; font-weight: 800; margin-top: -15px; text-transform: uppercase; }
    
    /* Boutons de paiement Premium avec Tarif */
    .pay-btn > div > button {
        background-color: #002147 !important;
        color: #00E5FF !important;
        border: 2px solid #00E5FF !important;
        font-size: 20px !important;
        height: 60px !important;
        width: 100%;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,229,255,0.2);
    }
    .stButton>button { border-radius: 10px !important; font-weight: bold; }
    .stButton>button:hover { background-color: #F3812B !important; color: white !important; }
    
    /* Footer Style */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        background-color: transparent !important; color: #999 !important; border: none !important; font-size: 11px !important; height: auto !important; padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS DE PRODUCTION ---
def extraire_texte(file):
    with pdfplumber.open(file) as pdf:
        return "".join([page.extract_text() for page in pdf.pages])

def export_cv_pdf(texte):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CV OPTIMISÉ - ZIPNGO ZAXX", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    # Nettoyage pour format PDF standard
    clean_txt = texte.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_txt)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. VARIABLES D'ÉTAT & 20 LANGUES ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", 
    "Português", "Mandarin", "Japonais", "Arabe", "Russe", 
    "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", 
    "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"
]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'footer_view' not in st.session_state: st.session_state.footer_view = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "login"

# --- 6. HEADER (LANGUES) ---
col_lang, _ = st.columns([1, 4])
with col_lang:
    st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

# --- 7. AUTHENTIFICATION ET RÉCUPÉRATION ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)

    if st.session_state.auth_mode == "recup":
        st.subheader("🔑 Récupération de compte")
        st.text_input("Email de connexion")
        if st.button("Recevoir le lien"): st.success("Lien envoyé !")
        if st.button("Changer l'email"): st.info("Contact support : creationsites06@gmail.com")
        if st.button("Retour"): st.session_state.auth_mode = "login"; st.rerun()
    else:
        t1, t2 = st.tabs(["Connexion", "Créer un compte"])
        with t1:
            e = st.text_input("Email", key="l_e")
            st.text_input("Mot de passe", type="password", key="l_p")
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e, "Candidat"
                st.rerun()
            if st.button("Mot de passe oublié ?"): st.session_state.auth_mode = "recup"; st.rerun()
        with t2:
            ne = st.text_input("Email", key="r_e")
            nr = st.radio("Type de profil :", ["Candidat", "Employeur"], horizontal=True)
            if st.button("S'inscrire 🚀"):
                st.session_state.user, st.session_state.role = ne, nr
                st.rerun()

# --- 8. DASHBOARD (TOUS LES OUTILS) ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user}**")
        if st.button("Déconnexion"): st.session_state.clear(); st.rerun()

    # SECTION PAIEMENT (90 JOURS)
    st.markdown("### 💎 Activation de votre Pass")
    tarif = "3 €" if st.session_state.role == "Candidat" else "49 €"
    st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
    if st.button(f"ACTIVER MON PASS 90 JOURS — {tarif}"):
        st.warning("Paiement immédiat sans remboursement. Activation en cours...")
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    if st.session_state.role == "Candidat":
        tab_v, tab_ia, tab_multi = st.tabs(["🎥 Pitch Vidéo", "🤖 Outils IA", "📢 Multidiffusion"])
        with tab_v:
            st.subheader("Entretien Vidéo (Pitch 30s)")
            st.camera_input("Enregistrez votre présentation")
            st.button("Valider et Publier")
        with tab_ia:
            st.subheader("Optimisation IA")
            f = st.file_uploader("CV (PDF)", type="pdf")
            if f:
                txt = extraire_texte(f)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("🔍 Scan ATS"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Score ATS: {txt}"}], model="llama3-8b-8192")
                        st.write(res.choices[0].message.content)
                with c2:
                    if st.button("✨ Relooking CV"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Réécris: {txt}"}], model="llama3-8b-8192")
                        relooke = res.choices[0].message.content
                        st.download_button("📥 Télécharger PDF", data=export_cv_pdf(relooke), file_name="CV_Zaxx.pdf")
                with c3:
                    if st.button("✍️ Lettre"):
                        res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Lettre: {txt}"}], model="llama3-8b-8192")
                        st.text_area("Lettre :", res.choices[0].message.content)
        with tab_multi:
            st.subheader("Multidiffusion Candidat")
            st.multiselect("Canaux :", ["LinkedIn", "Indeed", "HelloWork", "Zaxx Network"])
            if st.button("Lancer la multidiffusion 🚀"): st.success("Profil diffusé !")

    else: # EMPLOYEUR
        tab_src, tab_off = st.tabs(["🔍 Vidéothèque", "📢 Publier"])
        with tab_src:
            st.subheader("Sourcing Candidats")
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")
            st.button("Contacter ce profil")
        with tab_off:
            st.subheader("Multidiffuseur d'offres")
            st.text_area("Annonce")
            if st.button("Diffuser sur 20+ plateformes"): st.success("Offre publiée !")

# --- 9. FOOTER LÉGAL & RGPD ---
st.divider()
if st.session_state.footer_view == "mentions":
    st.info("⚖️ **MENTIONS :** Liliane RAKOTOBE. Contact : creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.")
elif st.session_state.footer_view == "cgv":
    st.info("📜 **CGV :** Pass 90j (49€ Recruteur / 3€ Candidat). Paiement immédiat sans remboursement. Mise en veille auto après 90 jours.")
elif st.session_state.footer_view == "rgpd":
    st.info("🔒 **RGPD :** Données et vidéos protégées. Traitement par IA confidentiel. Suppression sur demande.")

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
