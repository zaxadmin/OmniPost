import streamlit as st

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (DESIGN, SÉCURITÉ VIDÉO & FOOTER DISCRET) ---
st.markdown("""
<style>
    /* Identité Visuelle */
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 20px; font-weight: 800; margin-top: -20px; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Boutons Style Zaxx */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: translateY(-1px); }

    /* Alerte Statut Veille (Pass expiré) */
    .status-veille { background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; text-align: center; font-weight: bold; margin-bottom: 20px; }

    /* Sécurité Vidéo : Bloquer le téléchargement */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
    video::-webkit-media-controls-panel { width: calc(100% + 30px); }

    /* Style du Footer Discret */
    summary { cursor: pointer; font-weight: bold; color: #888; list-style: none; font-size: 13px; outline: none; }
    summary::-webkit-details-marker { display: none; }
    summary:hover { color: #F3812B; }
</style>
""", unsafe_allow_html=True)

# --- 3. LISTE DES 20 LANGUES ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", "Português", 
    "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", 
    "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", 
    "Suédois", "Indonésien"
]

# --- 4. GESTION DE SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'pass_actif' not in st.session_state: st.session_state.pass_actif = True

# --- 5. INTERFACE D'ACCUEIL ---
if not st.session_state.user:
    # Sélecteur de langue compact
    col_l, _ = st.columns([1, 4])
    with col_l:
        st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

    # Logo central
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    # Formulaire de connexion centré (compatible mobile/PC)
    _, col_centrale, _ = st.columns([0.2, 2, 0.2])
    with col_centrale:
        mode = st.tabs(["Connexion", "Créer un compte"])
        
        with mode[0]:
            e_in = st.text_input("Email")
            p_in = st.text_input("Mot de passe", type="password")
            r_in = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e_in, r_in
                st.rerun()

        with mode[1]:
            st.info("🎁 Inclus : Pass 3 mois de visibilité offert.")
            st.text_input("Email", key="reg_mail")
            st.checkbox("J'accepte les CGV et le Pass 3 mois")
            st.button("Activer mon Pass et m'inscrire 🚀")

# --- 6. ESPACES UTILISATEURS ---
else:
    with st.sidebar:
        st.markdown(f"### Espace {st.session_state.role}")
        st.write(f"👤 **{st.session_state.user}**")
        st.divider()
        st.selectbox("🌐 Langue interface", LISTE_LANGUES)
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()
        if st.button("Basculer Statut Pass (Test)"):
            st.session_state.pass_actif = not st.session_state.pass_actif

    # --- ESPACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        if not st.session_state.pass_actif:
            st.markdown('<div class="status-veille">⚠️ Pass 3 mois expiré : Votre CV est en VEILLE (invisible).</div>', unsafe_allow_html=True)
            st.button("Réactiver mon Pass 🚀")
        
        t1, t2 = st.tabs(["🪄 Coach IA", "🎥 Pitch Vidéo"])
        with t2:
            st.subheader("Ma Présentation Vidéo")
            if st.checkbox("Enregistrer un pitch (30s)"):
                st.info("La vidéo sera protégée contre le téléchargement.")
                st.button("🔴 Démarrer")

    # --- ESPACE EMPLOYEUR / RECRUTEUR ---
    else:
        st.subheader("Vidéothèque des Candidats")
        st.write("Visionnage sécurisé (Lecture seule)")
        # Exemple de vidéo sécurisée
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

# --- 7. FOOTER FINAL (ULTRA DISCRET & CLIQUABLE) ---
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
                <b>Hébergement :</b> Streamlit Cloud. <br>
                <b>Contact :</b> creationsites06@gmail.com.
            </div>
        </details>

        <details style="margin-bottom: 10px;">
            <summary>📜 CGV & Pass 3 Mois</summary>
            <div style="padding: 10px; background: white; border: 1px solid #eee; border-radius: 5px; margin-top: 5px; font-size: 11px; color: #555;">
                Accès via <b>Pass 3 mois</b> (90 jours). <br>
                <b>Mise en veille :</b> Sans renouvellement, le compte devient invisible. Pas de prélèvement automatique.
            </div>
        </details>

        <details style="margin-bottom: 10px;">
            <summary>🔒 RGPD & Confidentialité</summary>
            <div style="padding: 10px; background: white; border: 1px solid #eee; border-radius: 5px; margin-top: 5px; font-size: 11px; color: #555;">
                Vidéos protégées. Données chiffrées. <br>
                Droit de suppression totale sur simple demande ou via profil.
            </div>
        </details>

    </div>

    <p style="font-size: 10px; color: #ccc; margin-top: 20px;">© 2026 Zipngo-Zaxx | Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
