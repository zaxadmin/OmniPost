import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
import time

# --- 1. CONFIGURATION IA SÉCURISÉE ---
try:
    # Utilise la clé stockée dans .streamlit/secrets.toml ou sur le Cloud
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Clé API Groq introuvable. Vérifiez vos Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS (PRODUCTION) ---
st.markdown("""
<style>
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 18px; font-weight: 800; margin-top: -15px; text-transform: uppercase; }
    
    /* Boutons de paiement */
    .pay-btn > div > button {
        background-color: #002147 !important;
        color: #00E5FF !important;
        border: 2px solid #00E5FF !important;
        font-size: 20px !important;
        height: 60px !important;
        width: 100%;
        border-radius: 12px !important;
    }
    
    /* Boutons IA */
    .stButton>button { border-radius: 10px !important; font-weight: bold; }
    
    /* Liens Footer */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        background-color: transparent !important; color: #999 !important; border: none !important; font-size: 11px !important; height: auto !important; padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS TECHNIQUES ---
def extraire_texte_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])
    except Exception as e:
        return f"Erreur de lecture : {e}"

def generer_pdf_cv(texte_optimise):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CV OPTIMISÉ - ZAXX", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, texte_optimise.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION ---
LISTE_LANGUES = ["Français", "English", "Español", "Malagasy"]
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'footer_view' not in st.session_state: st.session_state.footer_view = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "login"

# --- 6. HEADER & AUTHENTIFICATION ---
col_l, _ = st.columns([1, 4])
with col_l: st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)

    if st.session_state.auth_mode == "recup":
        st.subheader("🔑 Récupération de compte")
        email_recup = st.text_input("Email oublié")
        if st.button("Envoyer le lien"): st.success("Lien de récupération envoyé !")
        if st.button("Retour"): st.session_state.auth_mode = "login"; st.rerun()
    else:
        t1, t2 = st.tabs(["Connexion", "Créer un compte"])
        with t1:
            e = st.text_input("Email", key="log_e")
            st.text_input("Mot de passe", type="password")
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e, "Candidat"
                st.rerun()
            if st.button("Mot de passe oublié ?"):
                st.session_state.auth_mode = "recup"; st.rerun()
        with t2:
            ne = st.text_input("Nouvel Email", key="reg_e")
            nr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
            if st.button("S'inscrire et commencer 🚀"):
                st.session_state.user, st.session_state.role = ne, nr
                st.rerun()

# --- 7. DASHBOARD PRODUCTION ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user}**")
        st.caption(f"Accès : {st.session_state.role}")
        if st.button("Déconnexion"): st.session_state.clear(); st.rerun()

    # --- ZONE PAIEMENT ---
    st.markdown("### 💎 Votre Pass 90 Jours")
    tarif = "3 €" if st.session_state.role == "Candidat" else "49 €"
    st.markdown(f'<div class="pay-btn">', unsafe_allow_html=True)
    if st.button(f"ACTIVER MES 90 JOURS — {tarif}"):
        st.info("🕒 Connexion au serveur de paiement immédiat sans remboursement...")
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # --- OUTILS CANDIDAT ---
    if st.session_state.role == "Candidat":
        tabs = st.tabs(["🎥 Vidéo Pitch", "🤖 IA & CV", "📢 Diffusion"])
        
        with tabs[0]:
            st.subheader("Entretien Vidéo (Pitch 30s)")
            st.camera_input("Enregistrez-vous pour les recruteurs")
        
        with tabs[1]:
            st.subheader("Traitement IA de votre CV")
            file = st.file_uploader("Chargez votre CV PDF", type="pdf")
            if file:
                texte_cv = extraire_texte_pdf(file)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("🔍 Scan ATS"):
                        with st.spinner("Analyse IA Groq..."):
                            prompt = f"Analyse ce CV, donne un score sur 100 et cite les 3 compétences manquantes : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                            st.write(res.choices[0].message.content)
                with c2:
                    if st.button("✨ Relooking"):
                        with st.spinner("Optimisation..."):
                            prompt = f"Réécris ce CV pour le rendre ultra-professionnel avec des 'Power Phrases' : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                            txt = res.choices[0].message.content
                            st.download_button("📥 Télécharger PDF Relooké", data=generer_pdf_cv(txt), file_name="CV_ZAXX_Optimise.pdf")
                with c3:
                    if st.button("✍️ Lettre"):
                        with st.spinner("Rédaction..."):
                            prompt = f"Rédige une lettre de motivation percutante pour ce profil : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                            st.text_area("Lettre générée :", res.choices[0].message.content, height=150)
        
        with tabs[2]:
            st.subheader("Multidiffusion Profil")
            st.multiselect("Diffuser vers :", ["LinkedIn", "Indeed", "HelloWork", "Zaxx Network"])
            if st.button("Lancer la multidiffusion 🚀"): st.success("Profil envoyé !")

    # --- OUTILS RECRUTEUR ---
    else:
        tabs = st.tabs(["🔍 Sourcing", "📢 Publier Offre"])
        with tabs[0]:
            st.subheader("Vidéothèque des candidats")
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                st.button("Contacter Marc L.")
            with col_v2:
                st.video("https://www.w3schools.com/html/movie.mp4")
                st.button("Contacter Sarah J.")
        with tabs[1]:
            st.subheader("Multidiffuseur d'offres")
            st.text_area("Détails du poste")
            if st.button("Diffuser sur 20+ plateformes"): st.success("Offre publiée partout !")

# --- 8. FOOTER DISCRET ---
st.divider()
if st.session_state.footer_view == "mentions":
    st.info("⚖️ **Mentions :** Liliane RAKOTOBE. creationsites06@gmail.com")
elif st.session_state.footer_view == "cgv":
    st.info("📜 **CGV :** Paiement immédiat sans remboursement. Pass 90j (3€/49€).")
elif st.session_state.footer_view == "rgpd":
    st.info("🔒 **RGPD :** Vidéos protégées. Suppression sur demande.")

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

st.markdown('<p style="text-align:center; font-size:10px; color:#ccc;">© 2026 Zipngo-Zaxx | Contact : RAKOTOBE Liliane</p>', unsafe_allow_html=True)
