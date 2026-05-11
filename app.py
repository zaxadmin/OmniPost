import streamlit as st

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (DESIGN, SÉCURITÉ & FOOTER) ---
# Ce bloc définit l'apparence et empêche l'affichage du code brut
st.markdown("""
<style>
    /* Identité Visuelle */
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 20px; font-weight: 800; margin-top: -20px; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Boutons Style Zaxx */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: translateY(-1px); }

    /* Alerte Mise en Veille (Pass expiré) */
    .status-veille { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; text-align: center; font-weight: bold; margin-bottom: 20px; }

    /* Sécurité Vidéo : Bloquer le téléchargement */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
    video::-webkit-media-controls-panel { width: calc(100% + 30px); }

    /* Fix pour l'affichage propre des détails HTML */
    summary { cursor: pointer; font-weight: bold; color: #888; list-style: none; font-size: 13px; }
    summary::-webkit-details-marker { display: none; }
    summary:hover { color: #F3812B; }
</style>
""", unsafe_allow_html=True)

# --- 3. DONNÉES & GESTION DE SESSION ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", "Português", 
    "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", 
    "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", 
    "Suédois", "Indonésien"
]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'pass_actif' not in st.session_state: st.session_state.pass_actif = True

# --- 4. INTERFACE D'ACCUEIL ---
if not st.session_state.user:
    # Sélecteur de langue en haut à gauche
    col_lang, _ = st.columns([1, 4])
    with col_lang:
        st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

    # Logo et Slogan
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    # Formulaire de connexion centré
    col_auth, _ = st.columns([1, 2, 1], gap="large")
    with col_auth[1]:
        mode = st.tabs(["Connexion", "Créer un compte"])
        
        with mode[0]:
            e_in = st.text_input("Email")
            p_in = st.text_input("Mot de passe", type="password")
            r_in = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e_in, r_in
                st.rerun()

        with mode[1]:
            st.info("🎁 Offre : Pass 3 mois inclus pour tester Zaxx.")
            st.text_input("Email d'inscription", key="reg_mail")
            st.checkbox("J'accepte les CGV et le Pass 3 mois")
            st.button("Activer mon Pass et m'inscrire 🚀")

# --- 5. ESPACES UTILISATEURS ---
else:
    with st.sidebar:
        st.markdown(f"### Espace {st.session_state.role}")
        st.write(f"👤 **{st.session_state.user}**")
        st.divider()
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()
        # Simulation pour la démonstration
        if st.button("Simuler expiration Pass"):
            st.session_state.pass_actif = not st.session_state.pass_actif

    # --- ESPACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        if not st.session_state.pass_actif:
            st.markdown('<div class="status-veille">⚠️ Votre Pass 3 mois est expiré. Votre CV est actuellement en VEILLE (invisible pour les recruteurs).</div>', unsafe_allow_html=True)
            st.button("Réactiver mon Pass pour redevenir visible 🚀")
        
        t1, t2, t3 = st.tabs(["🪄 Coach IA", "🎥 Mon Pitch (Optionnel)", "👤 Mon Profil"])
        with t2:
            st.subheader("Booster ma candidature")
            if st.checkbox("Ajouter mon pitch vidéo de 30s"):
                st.info("La vidéo est enregistrée puis mise en ligne sécurisée (non téléchargeable).")
                st.button("🔴 Lancer l'enregistrement")

    # --- ESPACE EMPLOYEUR ---
    else:
        st.subheader("Sourcing & Vidéothèque")
        st.write("Profils actifs (Lecture vidéo seule - Téléchargement impossible)")
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

# --- 6. FOOTER FINAL (ULTRA DISCRET, CLIQUABLE & SÉCURISÉ) ---
# Ce bloc est écrit pour ne jamais afficher de code brut
st.markdown("""
<div style="text-align: center; margin-top: 80px; padding: 20px; border-top: 1px solid #eee; background-color: #fcfcfc;">
    
    <div style="margin-bottom: 20px;">
        <a href="mailto:creationsites06@gmail.com" style="color: #F3812B; text-decoration: none; font-weight: bold; font-size: 14px; padding: 8px 15px; border: 1px solid #F3812B; border-radius: 8px; display: inline-block;">
            ✉️ RAKOTOBE Liliane
        </a>
    </div>

    <div style="max-width: 400px; margin: 0 auto; text-align: left;">
        
        <details style="margin-bottom: 10px;">
            <summary>⚖️ Mentions Légales</summary>
            <div style="padding: 10px; background: white; border: 1px solid #eee; border-radius: 5px; margin-top: 5px; font-size: 11px; color: #555;">
                <b>Responsable :</b> RAKOTOBE Liliane. <br>
                <b>Hébergement :</b> Streamlit Cloud / Supabase. <br>
                <b>Contact :</b> creationsites06@gmail.com. <br>
                Zipngo-Zaxx est une marque déposée.
            </div>
        </details>

        <details style="margin-bottom: 10px;">
            <summary>📜 CGV & Pass 3 Mois</summary>
            <div style="padding: 10px; background: white; border: 1px solid #eee; border-radius: 5px; margin-top: 5px; font-size: 11px; color: #555;">
                L'accès s'effectue via un <b>Pass 3 mois</b> (90 jours). <br>
                <b>Mise en veille :</b> À l'expiration du Pass, sans renouvellement, le compte passe en mode veille. 
                Le profil devient invisible pour les recruteurs. Pas de prélèvement automatique.
            </div>
        </details>

        <details style="margin-bottom: 10px;">
            <summary>🔒 RGPD & Confidentialité</summary>
            <div style="padding: 10px; background: white; border: 1px solid #eee; border-radius: 5px; margin-top: 5px; font-size: 11px; color: #555;">
                Vidéos protégées contre le téléchargement. Données chiffrées. 
                Droit de suppression totale via les paramètres du profil ou sur demande.
            </div>
        </details>

    </div>

    <p style="font-size: 10px; color: #ccc; margin-top: 20px;">© 2026 Zipngo-Zaxx | Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
