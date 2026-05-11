import streamlit as st
from datetime import datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (DESIGN PRO, FOOTER & SÉCURITÉ) ---
st.markdown("""
<style>
    /* Logo et Titres */
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    
    /* Boutons */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: translateY(-2px); }

    /* Alertes Statut (Mise en veille) */
    .status-veille { background-color: #fff3cd; color: #856404; padding: 20px; border-radius: 12px; border: 1px solid #ffeeba; margin-bottom: 25px; text-align: center; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }

    /* Footer Style Professionnel */
    .footer-container { text-align: center; font-size: 13px; color: #444; margin-top: 80px; padding: 50px 20px; border-top: 3px solid #002147; background-color: #f4f7f9; border-radius: 30px 30px 0 0; }
    .mailto-link { color: #F3812B !important; text-decoration: none; font-weight: bold; font-size: 16px; padding: 12px 25px; border: 2px solid #F3812B; border-radius: 12px; display: inline-block; transition: 0.3s; background: white; }
    .mailto-link:hover { background-color: #F3812B; color: white !important; }
    
    .legal-section { margin-top: 40px; text-align: left; max-width: 1000px; margin-left: auto; margin-right: auto; padding: 30px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
    .legal-title { font-weight: 800; color: #002147; text-transform: uppercase; font-size: 13px; margin-bottom: 10px; display: block; border-bottom: 2px solid #F3812B; width: fit-content; padding-bottom: 4px; }
    .legal-text { margin-bottom: 25px; line-height: 1.7; color: #333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    /* Sécurité Vidéo */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
    video::-webkit-media-controls-panel { width: calc(100% + 30px); }
</style>
""", unsafe_allow_html=True)

# --- 3. DONNÉES & LANGUES ---
LISTE_LANGUES = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'pass_actif' not in st.session_state: st.session_state.pass_actif = True 

# --- 4. INTERFACE D'ACCUEIL ---
if not st.session_state.user:
    col_lang, _ = st.columns([1, 4])
    with col_lang:
        st.selectbox("🌐 Langue / Language", LISTE_LANGUES, index=0)

    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col_auth, _ = st.columns([2, 2])
    with col_auth:
        mode = st.tabs(["Connexion", "Créer un compte"])
        
        with mode[0]:
            e_log = st.text_input("Email de connexion")
            p_log = st.text_input("Mot de passe", type="password")
            r_log = st.radio("Accès :", ["Employeur", "Candidat"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e_log, r_log
                st.rerun()

        with mode[1]:
            st.info("🎯 Accès complet via le Pass 3 mois (90 jours).")
            st.text_input("Email")
            st.text_input("Choisir un mot de passe", type="password")
            st.radio("Je suis :", ["Employeur", "Candidat"], horizontal=True, key="reg_role")
            st.checkbox("J'accepte les CGV et le principe du Pass 3 mois")
            st.button("Activer mon Pass et m'inscrire 🚀")

# --- 5. ESPACES CONNECTÉS ---
else:
    with st.sidebar:
        st.markdown(f"### Espace {st.session_state.role}")
        st.write(f"👤 {st.session_state.user}")
        st.divider()
        st.selectbox("🌐 Changer de langue", LISTE_LANGUES)
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()
        # Simulation d'expiration pour démo
        if st.button("Toggle Statut Pass (Démo)"):
            st.session_state.pass_actif = not st.session_state.pass_actif

    # --- ESPACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        if not st.session_state.pass_actif:
            st.markdown('<div class="status-veille">⚠️ Votre Pass 3 mois a expiré. Votre CV est actuellement en VEILLE (invisible pour les recruteurs).</div>', unsafe_allow_html=True)
            st.button("Réactiver mon Pass pour redevenir visible 🚀")
        
        c1, c2, c3 = st.tabs(["🪄 Coach IA", "🎥 Vidéo (Optionnel)", "👤 Mon Profil"])
        with c1:
            st.subheader("Optimisation de votre CV")
            st.text_area("Collez votre CV ici pour l'IA...")
        with c2:
            st.subheader("Pitch Vidéo")
            st.info("Le pitch vidéo est facultatif mais recommandé pour sortir du mode veille plus rapidement.")
            if st.checkbox("Je souhaite m'enregistrer"):
                st.button("🔴 Lancer l'enregistrement")

    # --- ESPACE RECRUTEUR ---
    else:
        t1, t2 = st.tabs(["📥 Candidatures", "📅 Entretiens"])
        with t1:
            st.subheader("Sourcing International")
            st.write("Visionnage des pitchs candidats (Lecture seule sécurisée).")
            st.video("https://www.w3schools.com/html/mov_bbb.mp4")

# --- 6. FOOTER FINAL (TEXTES RÉELS & MAILTO) ---
st.markdown("""
<div class="footer-container">
    <div style="margin-bottom: 30px;">
        © 2026 
        <a href="mailto:creationsites06@gmail.com" class="mailto-link">
            ✉️ RAKOTOBE Liliane
        </a>
    </div>

    <div class="legal-section">
        <div class="legal-text">
            <span class="legal-title">Mentions Légales</span>
            Responsable de publication : RAKOTOBE Liliane. 
            Plateforme technologique éditée via Streamlit Cloud. Base de données sécurisée sous Supabase. 
            Contact technique : creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.
        </div>

        <div class="legal-text">
            <span class="legal-title">CGV & Pass 3 Mois (Candidats et Recruteurs)</span>
            L'accès aux services Zipngo-Zaxx s'effectue par l'acquisition d'un <b>Pass 3 mois</b> (90 jours). 
            À l'expiration de ce délai, sans renouvellement de la part de l'utilisateur, le compte est placé en <b>mode veille</b>. 
            Pour le candidat, cela signifie que son CV et son profil deviennent invisibles pour les recruteurs. 
            Les données restent conservées de manière sécurisée pour permettre une réactivation ultérieure immédiate. 
            Il n'y a aucun renouvellement automatique ni prélèvement non consenti.
        </div>

        <div class="legal-text">
            <span class="legal-title">RGPD & Protection des Données</span>
            Nous appliquons une politique de transparence totale. Vos données personnelles sont utilisées exclusivement pour le recrutement. 
            Les vidéos de présentation (pitch) sont protégées par un protocole anti-téléchargement pour garantir votre droit à l'image. 
            Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression totale de vos données sur simple demande ou via votre espace profil.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
