import streamlit as st

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. STYLE CSS (DESIGN & SÉCURITÉ) ---
st.markdown("""
<style>
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 20px; font-weight: 800; margin-top: -20px; text-transform: uppercase; }
    
    /* Boutons standards */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; font-weight: bold; height: 45px; }
    
    /* Mini-boutons pour le footer (Discrétion totale) */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        background-color: transparent !important;
        color: #999 !important;
        border: none !important;
        font-size: 11px !important;
        height: auto !important;
        padding: 0 !important;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button:hover {
        color: #F3812B !important;
        text-decoration: underline !important;
    }

    /* Sécurité Vidéo */
    video::-internal-media-controls-download-button { display:none; }
    video::-webkit-media-controls-enclosure { overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIQUE & LANGUES ---
LISTE_LANGUES = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"]

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None
if 'view' not in st.session_state: st.session_state.view = None # Pour gérer l'affichage légal

# --- 4. ACCUEIL ---
if not st.session_state.user:
    col_l, _ = st.columns([1, 4])
    with col_l: st.selectbox("🌐", LISTE_LANGUES, label_visibility="collapsed")

    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    _, col_centrale, _ = st.columns([0.2, 2, 0.2])
    with col_centrale:
        mode = st.tabs(["Connexion", "Créer un compte"])
        with mode[0]:
            e = st.text_input("Email")
            r = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user, st.session_state.role = e, r
                st.rerun()
        with mode[1]:
            st.info("🎁 Pass 3 mois inclus.")
            st.button("S'inscrire 🚀")

# --- 5. DASHBOARDS (VIDÉOS & CONTENU) ---
else:
    with st.sidebar:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    if st.session_state.role == "Candidat":
        st.subheader("Espace Candidat")
    else:
        st.subheader("Espace Recruteur")
        st.video("https://www.w3schools.com/html/mov_bbb.mp4")

# --- 6. FOOTER DISCRET (SANS QUITTER LA PAGE) ---
st.divider()

# Affichage du contenu légal uniquement si cliqué (en haut du footer)
if st.session_state.view == "mentions":
    st.caption("⚖️ **Mentions Légales :** Responsable Liliane RAKOTOBE. Hébergement Streamlit Cloud. Contact : creationsites06@gmail.com")
elif st.session_state.view == "cgv":
    st.caption("📜 **CGV :** Pass 3 mois (90j). Mise en veille automatique après expiration. Pas de prélèvement automatique.")
elif st.session_state.view == "rgpd":
    st.caption("🔒 **RGPD :** Vidéos protégées. Droit de suppression totale sur demande.")

# Barre de liens footer
f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1, 1])

with f_col1:
    if st.button("Mentions Légales"): st.session_state.view = "mentions"; st.rerun()
with f_col2:
    if st.button("CGV & Pass"): st.session_state.view = "cgv"; st.rerun()
with f_col3:
    if st.button("RGPD"): st.session_state.view = "rgpd"; st.rerun()
with f_col4:
    if st.button("Masquer"): st.session_state.view = None; st.rerun()

st.markdown("""
<div style="text-align: center; margin-top: 10px;">
    <a href="mailto:creationsites06@gmail.com" style="color: #F3812B; text-decoration: none; font-size: 12px; font-weight: bold;">
        ✉️ Contact : RAKOTOBE Liliane
    </a>
    <p style="font-size: 10px; color: #ccc;">© 2026 Zipngo-Zaxx</p>
</div>
""", unsafe_allow_html=True)
