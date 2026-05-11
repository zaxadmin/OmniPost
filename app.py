import streamlit as st
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (DESIGN & SÉCURITÉ VIDÉO) ---
st.markdown("""
<style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; }
    .footer-text { text-align: center; font-size: 11px; color: gray; margin-top: 50px; padding: 20px; border-top: 1px solid #eee; }
    .footer-links a { color: #F3812B; text-decoration: none; margin: 0 10px; font-weight: bold; }
    .bannette-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; border-left: 5px solid #ddd; }
    .border-top { border-left-color: #2e7d32 !important; }
    .border-chance { border-left-color: #F3812B !important; }
    .instruction-note { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00E5FF; margin-bottom: 20px; font-size: 14px; }
    
    /* Sécurité Vidéo : Empêcher le téléchargement */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
    video::-webkit-media-controls-panel { width: calc(100% + 30px); }
</style>
""", unsafe_allow_html=True)

# --- 3. CONSTANTES ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", "Português", 
    "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", 
    "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", 
    "Suédois", "Indonésien"
]

# --- 4. INITIALISATION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'contact_email' not in st.session_state: st.session_state.contact_email = ""

# --- 5. AUTHENTIFICATION ---
if not st.session_state.user:
    col_l, _ = st.columns([1, 4])
    with col_l:
        st.selectbox("🌐 Langue / Language", LISTE_LANGUES, index=0)

    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col_auth, _ = st.columns([2, 2])
    with col_auth:
        mode = st.tabs(["Connexion", "Créer un compte"])
        
        with mode[0]:
            e_login = st.text_input("Email de connexion")
            p_login = st.text_input("Mot de passe", type="password")
            r_login = st.radio("Accès :", ["Employeur", "Candidat"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e_login, r_login
                st.session_state.contact_email = e_login
                st.rerun()
            st.button("Mot de passe oublié ?", type="secondary")

        with mode[1]:
            st.text_input("Email souhaité")
            st.text_input("Mot de passe", type="password", key="reg_p")
            st.radio("Rôle :", ["Employeur", "Candidat"], horizontal=True, key="reg_r")
            st.checkbox("J'accepte les Conditions Générales de Vente (CGV)")
            st.checkbox("J'accepte la Politique de Confidentialité")
            st.button("Créer mon compte 🚀")

# --- 6. ESPACES UTILISATEURS ---
else:
    with st.sidebar:
        st.markdown('<p style="font-size:25px; font-weight:900; color:#002147;">zaxx</p>', unsafe_allow_html=True)
        st.write(f"👤 **Identifiant :** {st.session_state.user}")
        st.write(f"📨 **Réception :** {st.session_state.contact_email}")
        st.divider()
        st.selectbox("🌐 Changer de langue", LISTE_LANGUES)
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- ESPACE EMPLOYEUR ---
    if st.session_state.role == "Employeur":
        t1, t2, t3, t4 = st.tabs(["📢 Publier", "📥 Sourcing", "📅 Entretiens Vidéo", "⚙️ Mon Compte"])
        
        with t1:
            st.subheader("Diffusion Assistée")
            st.text_input("Poste")
            st.multiselect("Langues requises", LISTE_LANGUES)
            st.button("Lancer le Multipostage IA 🚀")

        with t2:
            st.subheader("Candidatures & Pitchs")
            st.markdown("<div class='bannette-card border-chance'><b>Candidat #007</b> (2ème Chance - Pitch dispo 🎥)</div>", unsafe_allow_html=True)
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")
            st.caption("🔒 Lecture seule (Téléchargement désactivé)")

        with t3:
            st.subheader("Programmer un Entretien Vidéo")
            st.date_input("Choisir une date")
            st.time_input("Choisir une heure")
            st.button("Envoyer l'invitation au candidat ✉️")

        with t4:
            st.subheader("Gestion des Emails")
            new_c = st.text_input("Email de réception des CV", value=st.session_state.contact_email)
            if st.button("Enregistrer l'email opérationnel"):
                st.session_state.contact_email = new_c
                st.rerun()

    # --- ESPACE CANDIDAT ---
    else:
        c1, c2, c3, c4 = st.tabs(["🪄 Coach IA", "🎥 Pitch (Optionnel)", "📩 Mes RDV", "👤 Profil"])
        
        with c1:
            st.subheader("Analyse de CV")
            st.text_area("Collez votre CV")
            st.button("Optimiser mon profil ✨")

        with c2:
            st.subheader("Pitch Vidéo (Facultatif)")
            st.markdown('<div class="instruction-note">Présentez-vous en 30s. Non obligatoire, mais booste votre visibilité.</div>', unsafe_allow_html=True)
            if st.checkbox("Je souhaite m'enregistrer"):
                st.button("🔴 Démarrer l'enregistrement")

        with c3:
            st.subheader("Invitations à l'entretien")
            st.info("Aucun rendez-vous planifié pour le moment.")

        with c4:
            st.subheader("Mes Contacts")
            new_cc = st.text_input("Email pour recevoir les offres", value=st.session_state.contact_email)
            if st.button("Sauvegarder mes coordonnées"):
                st.session_state.contact_email = new_cc
                st.rerun()

# --- 7. FOOTER UNIVERSEL ---
st.markdown("""
<div class="footer-text">
    <b>© 2026 RAKOTOBE Liliane - Zipngo-Zaxx</b><br>
    <i>Antananarivo - Paris - Monde</i><br><br>
    <div class="footer-links">
        <a href="#">CGV</a> | <a href="#">Mentions Légales</a> | <a href="#">RGPD</a> | <a href="#">Aide</a>
    </div>
</div>
""", unsafe_allow_html=True)
