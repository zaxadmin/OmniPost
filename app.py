import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

st.markdown("""
    <style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin: 0; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; }
    .legend-box { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; display: flex; justify-content: space-around; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; font-size: 13px; margin: 5px; }
    .dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .source-tag-ext { background-color: #e3f2fd; color: #1976d2; padding: 3px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; border: 1px solid #1976d2; }
    .source-tag-zip { background-color: #f3e5f5; color: #7b1fa2; padding: 3px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; border: 1px solid #7b1fa2; }
    .tag-free { background-color: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }
    .tag-account { background-color: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }
    .bannette-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #ddd; }
    .border-top { border-left-color: #2e7d32 !important; }
    .border-chance { border-left-color: #F3812B !important; }
    .instruction-note { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00E5FF; margin-bottom: 20px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DONNÉES ---
LISTE_LANGUES = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", "Suédois", "Indonésien"]

DIFFUSEURS = {
    "France 🇫🇷": {"France Travail": "Inclus", "Apec": "Inclus", "Hellowork": "Compte Pro", "Leboncoin": "Compte Pro"},
    "Madagascar 🇲🇬": {"PortalJob-mga": "Compte Pro", "Mada-Travail": "Inclus", "Tanajob": "Inclus"},
    "International 🌐": {"LinkedIn Pro": "Compte Pro", "Indeed": "Inclus", "Remote.com": "Compte Pro"}
}

# --- 3. CONNEXION ---
try:
    supabase = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
except:
    st.warning("Configuration Supabase manquante.")

if 'user' not in st.session_state: st.session_state.user = None

# --- 4. AUTHENTIFICATION ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col_auth, _ = st.columns([2, 2])
    with col_auth:
        with st.expander("🔑 Accès Espace Personnel", expanded=True):
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            role = st.radio("Je suis :", ["Employeur", "Candidat"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user = email
                st.session_state.role = role
                st.rerun()

# --- 5. DASHBOARDS ---
else:
    with st.sidebar:
        st.markdown('<p style="font-size:25px; font-weight:900; color:#002147;">zaxx</p>', unsafe_allow_html=True)
        st.write(f"👤 {st.session_state.user}")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- MODE EMPLOYEUR ---
    if st.session_state.role == "Employeur":
        t1, t2, t3 = st.tabs(["📢 Publier", "📥 Sourcing", "⚙️ Comptes"])
        
        with t1:
            st.subheader("Créer une annonce")
            titre = st.text_input("Poste")
            lieu = st.text_input("Ville/Pays")
            notes = st.text_area("Détails (Missions, etc.)")
            if st.button("IA : Rédiger l'annonce 🪄"):
                st.session_state.txt = f"JOB : {titre}\nLIEU : {lieu}\n{notes}"
            
            job_final = st.text_area("Texte final", value=st.session_state.get('txt', ""), height=150)
            
            st.divider()
            st.subheader("Diffusion")
            pays = st.multiselect("Pays", list(DIFFUSEURS.keys()), default=["France 🇫🇷"])
            if st.button("Diffuser Partout 🚀"):
                st.success("Diffusion réussie !")

        with t2:
            st.subheader("🎨 Guide Couleurs")
            st.markdown("""<div class="legend-box">
                <div class="legend-item"><span class="dot" style="background-color: #1976d2;"></span> <b>Bleu :</b> Extérieur</div>
                <div class="legend-item"><span class="dot" style="background-color: #7b1fa2;"></span> <b>Violet :</b> Base Zipngo</div>
                <div class="legend-item"><span class="dot" style="background-color: #2e7d32;"></span> <b>Vert :</b> Top Match</div>
                <div class="legend-item"><span class="dot" style="background-color: #F3812B;"></span> <b>Orange :</b> 2ème Chance</div>
            </div>""", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 📬 Postulants")
                st.markdown("<div class='bannette-card border-top'><span class='source-tag-ext'>EXT</span> <b>Jean D.</b></div>", unsafe_allow_html=True)
            with c2:
                st.markdown("### 🔍 Suggestions Zipngo")
                st.markdown("<div class='bannette-card border-chance'><span class='source-tag-zip'>ZIP</span> <b>Profil #441</b></div>", unsafe_allow_html=True)

        with t3:
            st.subheader("Comptes Agences")
            for i in range(1, 4):
                st.text_input(f"Agence {i}", key=f"ag_{i}")

    # --- MODE CANDIDAT ---
    elif st.session_state.role == "Candidat":
        c_ia, c_vid, c_jobs = st.tabs(["🪄 Coach IA", "🎥 Vidéo", "💼 Suivi"])
        
        with c_ia:
            st.subheader("Optimisation CV")
            st.text_area("Copiez votre CV")
            if st.button("Analyser ✨"):
                st.info("L'IA suggère d'ajouter vos langues.")

        with c_vid:
            st.subheader("Pitch Vidéo")
            st.info("📹 Prêt à enregistrer votre vidéo de 30 secondes.")
            if st.button("Démarrer l'enregistrement 🔴"):
                st.write("Enregistrement en cours...")

        with c_jobs:
            st.subheader("Mes candidatures")
            st.write("Aucune candidature envoyée pour le moment.")

# --- 6. FOOTER ---
st.markdown("<div style='text-align:center; font-size:11px; color:gray; margin-top:50px;'>© 2026 RAKOTOBE Liliane - Zipngo-Zaxx</div>", unsafe_allow_html=True)
