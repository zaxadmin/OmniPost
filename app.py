import streamlit as st

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (MINIMALISTE & SÉCURISÉ) ---
st.markdown("""
<style>
    /* Identité Visuelle */
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Boutons */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; font-weight: bold; border: none; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; }

    /* Alerte Statut Veille */
    .status-veille { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; text-align: center; font-weight: bold; margin-bottom: 20px; }

    /* FOOTER ULTRA DISCRET ET ÉTROIT */
    .footer-container { 
        text-align: center; 
        margin-top: 100px; 
        padding: 20px; 
        border-top: 1px solid #eee; 
        background-color: #fcfcfc;
        color: #999;
    }
    
    .mailto-link { 
        color: #F3812B !important; 
        text-decoration: none; 
        font-weight: bold; 
        font-size: 13px;
        padding: 5px 10px;
        border: 1px solid #F3812B;
        border-radius: 5px;
    }

    .legal-box {
        max-width: 500px; /* Force la discrétion en limitant la largeur */
        margin: 15px auto; 
        text-align: left;
    }

    details { 
        margin-bottom: 5px; 
        font-size: 12px; 
    }
    
    summary { 
        font-weight: 600; 
        cursor: pointer; 
        list-style: none;
        color: #888;
        outline: none;
    }
    
    summary:hover { color: #F3812B; }
    summary::-webkit-details-marker { display: none; }

    .legal-content { 
        padding: 12px; 
        background: white; 
        border: 1px solid #f0f0f0; 
        border-radius: 5px; 
        font-size: 11px; 
        color: #555;
        line-height: 1.5;
    }

    /* Sécurité Vidéo */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
    video::-webkit-media-controls-panel { width: calc(100% + 30px); }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE DE SESSION & LANGUES ---
LISTE_LANGUES = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'pass_actif' not in st.session_state: st.session_state.pass_actif = True

# --- 4. INTERFACE D'ACCUEIL ---
if not st.session_state.user:
    col_l, _ = st.columns([1, 4])
    with col_l: st.selectbox("🌐", LISTE_LANGUES)
    
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col_auth, _ = st.columns([2, 2])
    with col_auth:
        mode = st.tabs(["Connexion", "Créer un compte"])
        with mode[0]:
            e = st.text_input("Email")
            r = st.radio("Rôle", ["Candidat", "Employeur"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e, r
                st.rerun()
        with mode[1]:
            st.info("Pass 3 mois inclus pour tester la plateforme.")
            st.checkbox("J'accepte les CGV et le Pass 3 mois")
            st.button("Activer mon Pass 🚀")

# --- 5. DASHBOARDS ---
else:
    with st.sidebar:
        st.markdown(f"### Espace {st.session_state.role}")
        st.write(f"👤 {st.session_state.user}")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()
        # Bouton démo pour simuler l'expiration
        if st.button("Simuler expiration Pass"):
            st.session_state.pass_actif = not st.session_state.pass_actif

    # --- ESPACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        if not st.session_state.pass_actif:
            st.markdown('<div class="status-veille">⚠️ Votre Pass 3 mois est expiré. Votre profil est en VEILLE (invisible pour les recruteurs).</div>', unsafe_allow_html=True)
            st.button("Réactiver mon Pass 🚀")
        
        t1, t2 = st.tabs(["🪄 Coach IA", "🎥 Vidéo"])
        with t2:
            st.subheader("Pitch Vidéo (Optionnel)")
            if st.checkbox("S'enregistrer (30s)"):
                st.button("🔴 Démarrer Caméra")

    # --- ESPACE RECRUTEUR ---
    else:
        st.subheader("Sourcing Candidats")
        st.write("Visionnage sécurisé (Téléchargement bloqué)")
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

# --- 6. FOOTER MINIATURE & CLIQUABLE ---
st.markdown("""
<div class="footer-container">
    <div style="margin-bottom: 15px;">
        <a href="mailto:creationsites06@gmail.com" class="mailto-link">
            ✉️ RAKOTOBE Liliane
        </a>
    </div>

    <div class="legal-box">
        <details>
            <summary>⚖️ Mentions Légales</summary>
            <div class="legal-content">
                <b>Responsable :</b> RAKOTOBE Liliane. 
                Hébergement : Streamlit Cloud. Données : Supabase. 
                Contact : creationsites06@gmail.com. Zipngo-Zaxx est une marque déposée.
            </div>
        </details>

        <details>
            <summary>📜 CGV & Pass 3 Mois</summary>
            <div class="legal-content">
                L'accès s'effectue via un <b>Pass 3 mois</b> (90 jours). 
                À l'expiration, sans renouvellement, le compte passe en <b>mode veille</b>. 
                Le profil devient invisible pour les recruteurs. Pas de prélèvement automatique.
            </div>
        </details>

        <details>
            <summary>🔒 RGPD & Confidentialité</summary>
            <div class="legal-content">
                Vidéos protégées contre le téléchargement. Données chiffrées. 
                Droit de suppression totale disponible via les paramètres du profil.
            </div>
        </details>
    </div>
    
    <p style="font-size: 10px; color: #ccc; margin-top: 15px;">© 2026 Zipngo-Zaxx | Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
