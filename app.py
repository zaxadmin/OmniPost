import streamlit as st
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (DESIGN, FOOTER & SÉCURITÉ VIDÉO) ---
st.markdown("""
<style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; }
    
    /* Footer Style Professionnel */
    .footer-container { text-align: center; font-size: 12px; color: #444; margin-top: 60px; padding: 30px; border-top: 2px solid #002147; background-color: #f9f9f9; border-radius: 10px 10px 0 0; }
    .mailto-link { color: #F3812B !important; text-decoration: none; font-weight: bold; font-size: 15px; border: 1px solid #F3812B; padding: 5px 10px; border-radius: 5px; transition: 0.3s; }
    .mailto-link:hover { background-color: #F3812B; color: white !important; }
    .legal-section { margin-top: 20px; text-align: left; max-width: 900px; margin-left: auto; margin-right: auto; padding: 20px; background: white; border-radius: 8px; border: 1px solid #ddd; line-height: 1.6; }
    .legal-title { font-weight: bold; color: #002147; text-transform: uppercase; font-size: 11px; margin-top: 15px; display: block; border-bottom: 1px solid #eee; padding-bottom: 3px; }
    
    /* Bannettes de tri */
    .bannette-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; border-left: 5px solid #ddd; }
    .border-top { border-left-color: #2e7d32 !important; }
    .border-chance { border-left-color: #F3812B !important; }
    .instruction-note { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00E5FF; margin-bottom: 20px; font-size: 14px; }

    /* Sécurité Vidéo : Désactiver le téléchargement */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
    video::-webkit-media-controls-panel { width: calc(100% + 30px); }
</style>
""", unsafe_allow_html=True)

# --- 3. DONNÉES ET LANGUES ---
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
            st.checkbox("J'accepte la Politique de Confidentialité & RGPD")
            st.button("Créer mon compte 🚀")

# --- 6. DASHBOARDS ---
else:
    with st.sidebar:
        st.markdown('<p style="font-size:25px; font-weight:900; color:#002147;">zaxx</p>', unsafe_allow_html=True)
        st.write(f"🔑 **ID :** {st.session_state.user}")
        st.write(f"📧 **Contact :** {st.session_state.contact_email}")
        st.divider()
        st.selectbox("🌐 Changer de langue", LISTE_LANGUES)
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- ESPACE RECRUTEUR ---
    if st.session_state.role == "Employeur":
        t1, t2, t3, t4 = st.tabs(["📢 Publier", "📥 Sourcing", "📅 RDV Vidéo", "⚙️ Mon Compte"])
        
        with t1:
            st.subheader("Diffusion d'offre IA")
            st.text_input("Poste")
            st.multiselect("Langues requises", LISTE_LANGUES)
            st.button("Multipostage 🚀")

        with t2:
            st.subheader("Candidatures reçues")
            st.markdown("<div class='bannette-card border-top'><b>Candidat #007</b> (Top Match)</div>", unsafe_allow_html=True)
            st.write("🎥 **Pitch Vidéo (Lecture seule)**")
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")
            st.caption("🔒 Protection Zipngo : Téléchargement bloqué.")

        with t3:
            st.subheader("Planifier un entretien")
            st.date_input("Date du rendez-vous")
            st.button("Envoyer l'invitation vidéo")

        with t4:
            st.subheader("Paramètres")
            st.session_state.contact_email = st.text_input("Email de réception des CV", value=st.session_state.contact_email)
            st.button("Mettre à jour")

    # --- ESPACE CANDIDAT ---
    else:
        c1, c2, c3, c4 = st.tabs(["🪄 Coach IA", "🎥 Pitch (Optionnel)", "📩 Mes RDV", "👤 Mon Profil"])
        
        with c2:
            st.subheader("Pitch Vidéo (Facultatif)")
            st.markdown('<div class="instruction-note">Présentez-vous en 30s pour booster votre profil. Non obligatoire.</div>', unsafe_allow_html=True)
            if st.checkbox("Activer l'enregistrement"):
                st.button("🔴 Démarrer la caméra")

        with c4:
            st.subheader("Coordonnées")
            st.session_state.contact_email = st.text_input("Email de contact recruteur", value=st.session_state.contact_email)
            st.button("Sauvegarder")

# --- 7. FOOTER FINAL AVEC TEXTES LÉGAUX ET MAILTO ---
st.markdown("""
<div class="footer-container">
    <div>
        © 2026 
        <a href="mailto:creationsites06@gmail.com" class="mailto-link">
            ✉️ RAKOTOBE Liliane
        </a>
    </div>

    <div class="legal-section">
        <span class="legal-title">Mentions Légales</span>
        Responsable de publication : RAKOTOBE Liliane. 
        Plateforme hébergée par Streamlit Cloud. Base de données sécurisée via Supabase. 
        Contact technique : creationsites06@gmail.com. Toute reproduction du concept Zaxx est interdite.

        <span class="legal-title">CGV (Conditions Générales de Vente)</span>
        Zipngo-Zaxx fournit une solution technique de mise en relation entre recruteurs et candidats. 
        L'accès aux services premium pour les entreprises est soumis à un abonnement mensuel. 
        Nous ne garantissons pas l'embauche mais optimisons la pertinence des profils via nos algorithmes IA.

        <span class="legal-title">RGPD & Protection des Données</span>
        Vos données personnelles (email, CV) sont traitées dans l'unique but de faciliter votre recrutement. 
        Conformément à la loi, vous disposez d'un droit de retrait total de vos informations. 
        Les vidéos déposées sur la plateforme sont cryptées et ne peuvent être téléchargées par des tiers.
    </div>
</div>
""", unsafe_allow_html=True)
