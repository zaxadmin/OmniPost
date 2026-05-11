import streamlit as st

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (DESIGN PRO, FOOTER DISCRET & SÉCURITÉ) ---
st.markdown("""
<style>
    /* Logo et Titres */
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    
    /* Boutons Style Zaxx */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: translateY(-1px); }

    /* Alerte Mise en Veille */
    .status-veille { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; margin-bottom: 20px; text-align: center; font-weight: bold; }

    /* Footer Discret et Cliquable */
    .footer-container { text-align: center; margin-top: 80px; padding: 30px; border-top: 1px solid #eee; background-color: #f9f9f9; border-radius: 20px 20px 0 0; }
    .mailto-link { color: #F3812B !important; text-decoration: none; font-weight: bold; font-size: 15px; border: 1px solid #F3812B; padding: 6px 12px; border-radius: 8px; transition: 0.3s; }
    .mailto-link:hover { background-color: #F3812B; color: white !important; }
    
    /* Menus Accordéons (Détails) */
    details { text-align: left; max-width: 850px; margin: 8px auto; cursor: pointer; font-size: 13px; color: #555; }
    summary { font-weight: bold; color: #002147; outline: none; padding: 5px; list-style: none; transition: 0.2s; }
    summary:hover { color: #F3812B; }
    summary::-webkit-details-marker { display: none; }
    .legal-content { padding: 15px; background: white; border-radius: 8px; border: 1px solid #eee; line-height: 1.6; color: #444; margin-top: 5px; }

    /* Sécurité Vidéo : Bloquer le téléchargement */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
    video::-webkit-media-controls-panel { width: calc(100% + 30px); }
</style>
""", unsafe_allow_html=True)

# --- 3. CONSTANTES & SESSIONS ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", "Português", 
    "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", 
    "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", 
    "Suédois", "Indonésien"
]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'pass_actif' not in st.session_state: st.session_state.pass_actif = True

# --- 4. ACCUEIL & AUTHENTIFICATION ---
if not st.session_state.user:
    col_l, _ = st.columns([1, 4])
    with col_l: st.selectbox("🌐 Langue", LISTE_LANGUES, index=0)

    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col_auth, _ = st.columns([2, 2])
    with col_auth:
        mode = st.tabs(["Connexion", "Créer un compte"])
        with mode[0]:
            e_in = st.text_input("Email")
            r_in = st.radio("Rôle", ["Candidat", "Employeur"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e_in, r_in
                st.rerun()
        with mode[1]:
            st.info("🎁 Nouveau : Le Pass 3 mois est inclus pour tous les nouveaux inscrits.")
            st.checkbox("J'accepte les CGV et le Pass 3 mois")
            st.button("Activer mon Pass et m'inscrire 🚀")

# --- 5. DASHBOARDS ---
else:
    with st.sidebar:
        st.markdown(f"### Espace {st.session_state.role}")
        st.write(f"👤 {st.session_state.user}")
        st.divider()
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()
        # Simulation d'expiration pour le test
        if st.button("Toggle Statut Pass (Démo)"):
            st.session_state.pass_actif = not st.session_state.pass_actif

    # --- ESPACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        if not st.session_state.pass_actif:
            st.markdown('<div class="status-veille">⚠️ Votre Pass 3 mois a expiré. Votre CV est en VEILLE (invisible pour les recruteurs).</div>', unsafe_allow_html=True)
            st.button("Réactiver mon Pass 🚀")
        
        c1, c2, c3 = st.tabs(["🪄 Coach IA", "🎥 Pitch (Optionnel)", "👤 Mon Profil"])
        with c2:
            st.subheader("Votre Pitch Vidéo")
            if st.checkbox("Ajouter une présentation vidéo"):
                st.info("📹 Enregistrez 30s pour convaincre.")
                st.button("🔴 Démarrer")

    # --- ESPACE RECRUTEUR ---
    else:
        st.subheader("Sourcing & Recrutement")
        st.write("Visionnage des profils actifs (Lecture seule).")
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

# --- 6. FOOTER DISCRET & CLIQUABLE (MAINTENANCE LÉGALE) ---
st.markdown("""
<div class="footer-container">
    <div style="margin-bottom: 25px;">
        © 2026 
        <a href="mailto:creationsites06@gmail.com" class="mailto-link">
            ✉️ RAKOTOBE Liliane
        </a>
    </div>

    <div style="margin-top: 10px;">
        <details>
            <summary>⚖️ Mentions Légales</summary>
            <div class="legal-content">
                Responsable de publication : <b>RAKOTOBE Liliane</b>. 
                Plateforme technologique éditée via Streamlit Cloud. Base de données sécurisée via Supabase. 
                Contact technique : creationsites06@gmail.com. 
                Zipngo-Zaxx est une marque déposée.
            </div>
        </details>

        <details>
            <summary>📜 CGV & Pass 3 Mois</summary>
            <div class="legal-content">
                L'accès aux services Zipngo-Zaxx s'effectue via un <b>Pass 3 mois</b> (90 jours). 
                À l'expiration du Pass, sans renouvellement, le compte passe automatiquement en <b>mode veille</b>. 
                Pour le candidat, son CV et son profil deviennent invisibles pour les recruteurs. 
                Les données restent conservées pour une réactivation immédiate. Pas de prélèvement automatique.
            </div>
        </details>

        <details>
            <summary>🔒 RGPD & Confidentialité</summary>
            <div class="legal-content">
                Données personnelles utilisées exclusivement pour le recrutement. 
                Les vidéos (pitch) sont protégées par protocole anti-téléchargement. 
                Vous disposez d'un droit d'accès et de suppression totale via votre profil.
            </div>
        </details>
    </div>
</div>
""", unsafe_allow_html=True)
