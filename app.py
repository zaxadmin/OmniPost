import streamlit as st
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS ---
st.markdown("""
<style>
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 20px; font-weight: 800; margin-top: -20px; text-transform: uppercase; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; font-weight: bold; height: 45px; width: 100%; }
    .stButton>button:hover { background-color: #F3812B !important; }
    
    /* Style Spécifique Footer */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        background-color: transparent !important; color: #999 !important; border: none !important; font-size: 11px !important; height: auto !important; padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. INITIALISATION & LANGUES ---
LISTE_LANGUES = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'footer_view' not in st.session_state: st.session_state.footer_view = None
if 'paiement_en_cours' not in st.session_state: st.session_state.paiement_en_cours = False

# --- 4. FONCTION DE PAIEMENT FICTIF ---
def tunnel_paiement(prix, offre):
    st.session_state.paiement_en_cours = True
    st.warning(f"💳 Connexion sécurisée au tunnel de paiement (Mode Test)... Plan : {offre}")
    with st.spinner("Traitement de la transaction..."):
        time.sleep(2)
        st.success(f"✅ Paiement de {prix} accepté ! Votre Pass 3 mois est activé.")
        time.sleep(1)
    st.session_state.paiement_en_cours = False

# --- 5. INTERFACE D'ACCUEIL ---
if not st.session_state.user:
    col_l, _ = st.columns([1, 4])
    with col_l: st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    _, col_centrale, _ = st.columns([0.1, 2, 0.1])
    with col_centrale:
        mode = st.tabs(["Connexion", "Créer un compte"])
        with mode[0]:
            e = st.text_input("Email")
            r = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e, r
                st.rerun()
        with mode[1]:
            st.info("🎁 Inclus : Essai Recruteur (7j) ou Candidat (1j + Pack IA)")
            if st.button("Démarrer mon essai gratuit 🚀"):
                st.session_state.user = "Nouvel Utilisateur"
                st.session_state.role = "Candidat"
                st.rerun()

# --- 6. DASHBOARDS ---
else:
    with st.sidebar:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Déconnexion"):
            st.session_state.user = None; st.rerun()

    if st.session_state.role == "Candidat":
        st.subheader("🛠️ Outils IA (Essai 1 jour)")
        c1, c2, c3 = st.columns(3)
        with c1: st.button("🔍 Scan ATS")
        with c2: st.button("✨ Relooking CV")
        with c3: st.button("✍️ Lettre Motivation")
        
        st.divider()
        if st.button("💎 Activer le Pass 3 mois (Paiement Fictif)"):
            tunnel_paiement("29€", "Candidat 90 jours")

    else:
        st.subheader("🔍 Espace Recruteur (Essai 7 jours)")
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")
        if st.button("💎 S'abonner : Pass 3 mois (Paiement Fictif)"):
            tunnel_paiement("149€", "Recruteur 90 jours")

# --- 7. FOOTER DISCRET (CGV MISES À JOUR) ---
st.divider()

if st.session_state.footer_view == "mentions":
    st.info("⚖️ **Mentions Légales :** Responsable : RAKOTOBE Liliane. Éducation/Test via Streamlit Cloud. Contact : creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.")
elif st.session_state.footer_view == "cgv":
    st.info("""📜 **CGV & Pass :**
    \n **Recruteur :** Essai 7j gratuit. Pass 3 mois (90j) avec paiement immédiat (sans renouvellement tacite).
    \n **Candidat :** Essai 1j incluant : 1 scan ATS, 1 relooking, 1 lettre de motivation, 1 scan post-relooking et export PDF. Pass 3 mois (90j) avec mise en veille automatique après expiration.""")
elif st.session_state.footer_view == "rgpd":
    st.info("🔒 **RGPD :** Vidéo et données protégées. Suppression de compte sur simple demande.")

f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1, 0.5])
with f_col1:
    if st.button("Mentions Légales"): st.session_state.footer_view = "mentions"; st.rerun()
with f_col2:
    if st.button("CGV & Pass"): st.session_state.footer_view = "cgv"; st.rerun()
with f_col3:
    if st.button("RGPD"): st.session_state.footer_view = "rgpd"; st.rerun()
with f_col4:
    if st.session_state.footer_view:
        if st.button("✖️"): st.session_state.footer_view = None; st.rerun()

st.markdown("""
<div style="text-align: center; margin-top: 10px;">
    <p style="font-size: 11px; color: #999;">✉️ Contact : RAKOTOBE Liliane | © 2026 Zipngo-Zaxx</p>
</div>
""", unsafe_allow_html=True)
