import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
import time

# --- 1. CONFIGURATION IA SÉCURISÉE (VIA SECRETS.TOML) ---
try:
    # Récupère la clé 'GROQ_API_KEY' configurée dans tes secrets
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Configuration IA manquante. Vérifiez vos Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS (DESIGN PROFESSIONNEL) ---
st.markdown("""
<style>
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 18px; font-weight: 800; margin-top: -15px; text-transform: uppercase; }
    
    /* Boutons de paiement Premium */
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
    
    /* Style général boutons */
    .stButton>button { border-radius: 10px !important; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #F3812B !important; color: white !important; }
    
    /* Footer discret */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        background-color: transparent !important; color: #999 !important; border: none !important; font-size: 11px !important; height: auto !important; padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS TECHNIQUES (PRODUCTION) ---
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
    pdf.cell(0, 10, "CV OPTIMISÉ - ZIPNGO ZAXX", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    # Remplacement des caractères spéciaux pour éviter les erreurs PDF
    texte_propre = texte_optimise.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, texte_propre)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION DES VARIABLES D'ÉTAT ---
LISTE_LANGUES = ["Français", "English", "Español", "Malagasy"]
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'footer_view' not in st.session_state: st.session_state.footer_view = None
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = "login"

# --- 6. HEADER & LANGUES ---
col_l, _ = st.columns([1, 4])
with col_l:
    st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

# --- 7. SYSTÈME D'AUTHENTIFICATION ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)

    if st.session_state.auth_mode == "recup":
        st.subheader("🔑 Récupération de compte")
        email_recup = st.text_input("Saisissez votre email actuel")
        if st.button("Recevoir un lien de réinitialisation"):
            st.success(f"Un lien a été envoyé à {email_recup} (Simulation)")
        if st.button("Changer mon email de connexion"):
            st.info("Veuillez contacter le support : creationsites06@gmail.com")
        if st.button("Retour à la connexion"):
            st.session_state.auth_mode = "login"; st.rerun()
    else:
        t1, t2 = st.tabs(["Connexion", "Créer un compte"])
        with t1:
            e = st.text_input("Email", key="log_e")
            st.text_input("Mot de passe", type="password", key="log_p")
            if st.button("Se connecter 👍"):
                if e:
                    st.session_state.user, st.session_state.role = e, "Candidat"
                    st.rerun()
            if st.button("Mot de passe oublié ?", help="Cliquez pour réinitialiser"):
                st.session_state.auth_mode = "recup"; st.rerun()
        with t2:
            ne = st.text_input("Votre Email", key="reg_e")
            st.text_input("Mot de passe", type="password", key="reg_p")
            nr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
            if st.button("S'inscrire et accéder aux outils 🚀"):
                if ne:
                    st.session_state.user, st.session_state.role = ne, nr
                    st.rerun()

# --- 8. DASHBOARD PRODUCTION (UTILISATEUR CONNECTÉ) ---
else:
    with st.sidebar:
        st.write(f"👤 Connecté : **{st.session_state.user}**")
        st.caption(f"Espace {st.session_state.role}")
        if st.button("Déconnexion"):
            st.session_state.clear(); st.rerun()

    # --- BLOC PAIEMENT (BOUTONS AVEC TARIFS) ---
    st.markdown("### 💎 Activation du Pass 90 Jours")
    tarif = "3 €" if st.session_state.role == "Candidat" else "49 €"
    st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
    if st.button(f"ACTIVER MES 90 JOURS — {tarif}"):
        st.warning("⚠️ Redirection sécurisée en cours... Paiement immédiat sans remboursement.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # --- LOGIQUE CANDIDAT ---
    if st.session_state.role == "Candidat":
        tab_v, tab_ia, tab_diff = st.tabs(["🎥 Pitch Vidéo", "🤖 Intelligence Artificielle", "📢 Multidiffusion"])
        
        with tab_v:
            st.subheader("Votre Pitch Vidéo (30-60s)")
            st.info("Cette vidéo sera le premier élément vu par les recruteurs.")
            st.camera_input("Enregistrer mon entretien")
            st.button("Publier mon profil vidéo")

        with tab_ia:
            st.subheader("Outils de Production IA")
            file = st.file_uploader("Chargez votre CV au format PDF", type="pdf")
            if file:
                texte_cv = extraire_texte_pdf(file)
                st.success("Lecture du CV terminée.")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("🔍 Lancer le Scan ATS"):
                        with st.status("Analyse IA en cours..."):
                            p = f"Analyse ce CV et donne un score ATS sur 100 ainsi que les mots-clés manquants : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": p}], model="llama3-8b-8192")
                            st.write(res.choices[0].message.content)
                with c2:
                    if st.button("✨ Relooking & Export"):
                        with st.status("Génération du design..."):
                            p = f"Réécris ce CV avec des Power Phrases percutantes : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": p}], model="llama3-8b-8192")
                            txt_opt = res.choices[0].message.content
                            st.download_button("📥 Télécharger mon CV ZAXX (PDF)", data=generer_pdf_cv(txt_opt), file_name="CV_Zaxx_Optimise.pdf")
                with c3:
                    if st.button("✍️ Lettre de Motivation"):
                        with st.status("Rédaction IA..."):
                            p = f"Rédige une lettre de motivation captivante pour ce profil : {texte_cv}"
                            res = client_ia.chat.completions.create(messages=[{"role": "user", "content": p}], model="llama3-8b-8192")
                            st.text_area("Votre lettre :", res.choices[0].message.content, height=200)

        with tab_diff:
            st.subheader("Diffusion de profil")
            st.multiselect("Canaux de diffusion :", ["LinkedIn", "Indeed", "HelloWork", "Zaxx Network"])
            if st.button("Lancer la multidiffusion 🚀"):
                st.success("Profil envoyé aux plateformes partenaires !")

    # --- LOGIQUE RECRUTEUR ---
    else:
        tab_src, tab_off = st.tabs(["🔍 Sourcing Vidéo", "📢 Multidiffuseur Offres"])
        with tab_src:
            st.subheader("Vidéothèque Candidats")
            col1, col2 = st.columns(2)
            with col1:
                st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                st.button("Contacter Marc L.")
            with col2:
                st.video("https://www.w3schools.com/html/movie.mp4")
                st.button("Contacter Sarah J.")
        with tab_off:
            st.subheader("Publier une offre")
            st.text_area("Détails de l'annonce")
            if st.button("Diffuser sur 20+ Jobboards"):
                st.success("Annonce publiée sur l'ensemble du réseau !")

# --- 9. FOOTER LÉGAL ET RGPD ---
st.divider()

if st.session_state.footer_view == "mentions":
    st.info("""
    ⚖️ **MENTIONS LÉGALES**
    - **Responsable de la publication :** Liliane RAKOTOBE.
    - **Contact :** creationsites06@gmail.com
    - **Propriété :** Zipngo-Zaxx est une marque déposée.
    """)
elif st.session_state.footer_view == "cgv":
    st.info("""
    📜 **CGV & TARIFS (PASS 90 JOURS)**
    - **Tarif :** Recruteur 49 € / Candidat 3 €.
    - **Paiement :** Règlement immédiat sans remboursement possible compte tenu de la nature numérique du service.
    - **Validité :** Pass valable 90 jours. À l'issue, l'accès est suspendu et le profil candidat est mis en veille automatique.
    """)
elif st.session_state.footer_view == "rgpd":
    st.info("""
    🔒 **POLITIQUE RGPD**
    - **Protection :** Vos données et vidéos sont sécurisées et visibles uniquement par les abonnés actifs.
    - **IA :** Vos CV sont analysés par une Intelligence Artificielle de manière confidentielle.
    - **Droit :** Suppression totale du compte et des vidéos sur simple demande à : creationsites06@gmail.com.
    """)

# NAVIGATION FOOTER
f1, f2, f3, f4 = st.columns([1, 1, 1, 0.5])
with f1: 
    if st.button("Mentions Légales"): st.session_state.footer_view = "mentions"; st.rerun()
with f2: 
    if st.button("CGV & Pass"): st.session_state.footer_view = "cgv"; st.rerun()
with f3: 
    if st.button("RGPD"): st.session_state.footer_view = "rgpd"; st.rerun()
with f4:
    if st.session_state.footer_view:
        if st.button("✖️"): st.session_state.footer_view = None; st.rerun()

st.markdown('<p style="text-align:center; font-size:10px; color:#ccc; margin-top:20px;">© 2026 Zipngo-Zaxx | Tous droits réservés</p>', unsafe_allow_html=True)
