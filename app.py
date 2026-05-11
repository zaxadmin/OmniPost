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
    st.error("⚠️ Configuration IA manquante. Veuillez configurer GROQ_API_KEY dans les Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS PROFESSIONNEL ---
st.markdown("""
<style>
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
    pdf.cell(0, 10, "CV OPTIMISÉ - ZIPNGO ZAXX", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    texte_propre = texte_optimise.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, texte_propre)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", 
    "Português", "Mandarin", "Japonais", "Arabe", "Russe", 
    "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", 
    "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"
]

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
        # Affichage de votre nouveau logo avec le pouce orange
        if os.path.exists("_20260511_163213.JPG"):
            st.image("_20260511_163213.JPG", use_column_width=True)
        else:
            st.markdown("<h1 style='text-align: center;'>zipngo👍</h1>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    with t1:
        e = st.text_input("Email", key="login_email")
        st.text_input("Mot de passe", type="password")
        if st.button("Se connecter 👍"):
            st.session_state.user, st.session_state.role = e, "Candidat"
            st.rerun()
        if st.button("Mot de passe oublié ?"):
            st.info("Un lien de récupération a été envoyé (Simulation).")
            
    with t2:
        ne = st.text_input("Email", key="reg_email")
        nr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("S'inscrire 🚀"):
            st.session_state.user, st.session_state.role = ne, nr
            st.rerun()

# --- 8. DASHBOARD ET GESTION DE VALIDITÉ ---
else:
    with st.sidebar:
        st.write(f"👤 **{st.session_state.user}**")
        st.caption(f"Espace {st.session_state.role}")
        if st.button("Déconnexion"):
            st.session_state.clear()
            st.rerun()

    # --- LOGIQUE DE VALIDITÉ (ESSAIS & PASS) ---
    if st.session_state.validite is None:
        st.subheader("🚀 Activez votre espace de production")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🎁 Mode Essai")
            duree_essai = "1 jour" if st.session_state.role == "Candidat" else "7 jours"
            if st.button(f"Démarrer l'essai ({duree_essai})"):
                jours = 1 if st.session_state.role == "Candidat" else 7
                st.session_state.validite = datetime.now() + timedelta(days=jours)
                st.rerun()
        with c2:
            st.markdown("### 💎 Mode Premium")
            prix = "3 €" if st.session_state.role == "Candidat" else "49 €"
            st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
            if st.button(f"ACTIVER LE PASS 90J — {prix}"):
                st.session_state.validite = datetime.now() + timedelta(days=90)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif datetime.now() > st.session_state.validite:
        st.error("⌛ Votre Pass a expiré. Votre profil est mis en veille.")
        prix_reac = "3 €" if st.session_state.role == "Candidat" else "49 €"
        st.markdown('<div class="pay-btn">', unsafe_allow_html=True)
        if st.button(f"🚀 RÉACTIVER POUR 90 JOURS — {prix_reac}"):
            st.session_state.validite = datetime.now() + timedelta(days=90)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- INTERFACE ACTIVE ---
        jours_restants = (st.session_state.validite - datetime.now()).days
        st.success(f"✅ Accès Actif : Il vous reste {jours_restants} jours.")
        
        if st.session_state.role == "Candidat":
            tabs = st.tabs(["🎥 Pitch Vidéo", "🤖 Outils IA", "📢 Multidiffusion"])
            with tabs[0]:
                st.subheader("Votre entretien vidéo")
                st.camera_input("Enregistrez votre Pitch 30s")
                st.button("Valider et Publier mon profil")
            with tabs[1]:
                st.subheader("Production IA")
                file = st.file_uploader("Charger votre CV (PDF)", type="pdf")
                if file:
                    texte_cv = extraire_texte_pdf(file)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔍 Scan ATS"):
                            with st.spinner("Analyse..."):
                                res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Analyse ATS: {texte_cv}"}], model="llama3-8b-8192")
                                st.write(res.choices[0].message.content)
                    with col2:
                        if st.button("✨ Relooking CV"):
                            with st.spinner("Optimisation..."):
                                res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Optimise ce CV: {texte_cv}"}], model="llama3-8b-8192")
                                txt_opt = res.choices[0].message.content
                                st.download_button("📥 Télécharger PDF", data=generer_pdf_cv(txt_opt), file_name="CV_Zaxx_IA.pdf")
                    with col3:
                        if st.button("✍️ Lettre de Motivation"):
                            with st.spinner("Rédaction..."):
                                res = client_ia.chat.completions.create(messages=[{"role":"user","content":f"Lettre motivation pour: {texte_cv}"}], model="llama3-8b-8192")
                                st.text_area("Résultat :", res.choices[0].message.content, height=200)
            with tabs[2]:
                st.subheader("Diffusion de profil")
                st.multiselect("Plateformes cibles :", ["LinkedIn", "Indeed", "HelloWork", "Zaxx Network"])
                if st.button("Lancer la multidiffusion 🚀"): st.success("Profil envoyé !")
        
        else:
            tabs = st.tabs(["🔍 Sourcing Vidéo", "📢 Publier Offre"])
            with tabs[0]:
                st.subheader("Vidéothèque des candidats")
                st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                st.button("Contacter ce candidat")
            with tabs[1]:
                st.subheader("Multidiffuseur d'offres")
                st.text_area("Descriptif du poste")
                if st.button("Diffuser sur 20+ jobboards"): st.success("Offre publiée !")

# --- 9. FOOTER LÉGAL (CGV / RGPD) ---
st.divider()

if st.session_state.footer_view == "mentions":
    st.info("⚖️ **MENTIONS LÉGALES** : Responsable Liliane RAKOTOBE. Contact : creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.")
elif st.session_state.footer_view == "cgv":
    st.info("📜 **CGV & PASS 90J** : Tarifs : 49€ (Recruteur) / 3€ (Candidat). Paiement immédiat sans remboursement. À l'expiration des 90 jours, le profil est mis en veille automatique jusqu'à réactivation.")
elif st.session_state.footer_view == "rgpd":
    st.info("🔒 **POLITIQUE RGPD** : Vos données et vidéos sont sécurisées. Les analyses de CV sont traitées par Intelligence Artificielle de manière confidentielle. Suppression de compte sur simple demande.")

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

st.markdown('<p style="text-align:center; font-size:10px; color:#ccc; margin-top:20px;">© 2026 Zipngo-Zaxx | Tous droits réservés</p>', unsafe_allow_html=True)
