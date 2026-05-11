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
    
    /* Guide des Couleurs & Légende */
    .legend-box { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; display: flex; justify-content: space-around; flex-wrap: wrap; }
    .legend-item { display: flex; align-items: center; font-size: 13px; margin: 5px; }
    .dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    
    /* Badges de Source & Tags */
    .source-tag-ext { background-color: #e3f2fd; color: #1976d2; padding: 3px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; border: 1px solid #1976d2; }
    .source-tag-zip { background-color: #f3e5f5; color: #7b1fa2; padding: 3px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; border: 1px solid #7b1fa2; }
    .tag-free { background-color: #e8f5e9; color: #2e7d32; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }
    .tag-account { background-color: #fff3e0; color: #e65100; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }

    /* Cartes Candidats */
    .bannette-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); border-left: 5px solid #ddd; }
    .border-top { border-left-color: #2e7d32 !important; }
    .border-chance { border-left-color: #F3812B !important; }
    
    .instruction-note { background-color: #f0f7ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00E5FF; margin-bottom: 20px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DONNÉES INTERNATIONALES ---
LISTE_LANGUES = [
    "Français", "English", "Español", "Deutsch", "Italiano", "Português", 
    "Mandarin", "Japonais", "Arabe", "Russe", "Hindi", "Bengali", 
    "Malagasy", "Coréen", "Turc", "Vietnamien", "Polonais", "Néerlandais", 
    "Suédois", "Indonésien"
]

DIFFUSEURS = {
    "France 🇫🇷": {"France Travail": "Inclus", "Apec": "Inclus", "Hellowork": "Compte Pro", "Leboncoin": "Compte Pro"},
    "Madagascar 🇲🇬": {"PortalJob-mga": "Compte Pro", "Mada-Travail": "Inclus", "Tanajob": "Inclus"},
    "USA 🇺🇸": {"Dice": "Compte Pro", "Monster": "Compte Pro", "ZipRecruiter": "Compte Pro"},
    "International 🌐": {"LinkedIn Pro": "Compte Pro", "Indeed": "Inclus", "Remote.com": "Compte Pro"}
}

# --- 3. CONNEXION SUPABASE ---
try:
    # Assure-toi que tes secrets sont bien configurés sur Streamlit Cloud
    supabase = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
except:
    st.warning("⚠️ Connexion Supabase en attente de configuration.")

if 'user' not in st.session_state: st.session_state.user = None

# --- 4. ACCUEIL & AUTHENTIFICATION ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col_l, col_r = st.columns(2)
    with col_l:
        with st.expander("🔑 Accès Utilisateur (Recruteur ou Candidat)", expanded=True):
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            role = st.radio("Je suis un :", ["Employeur", "Candidat"], horizontal=True)
            if st.button("Se connecter 👍"):
                st.session_state.user = email
                st.session_state.role = role
                st.session_state.free_slots = 5
                st.rerun()

# --- 5. DASHBOARD CONNECTÉ ---
else:
    with st.sidebar:
        st.markdown('<p style="font-size:25px; font-weight:900; color:#002147;">zaxx</p>', unsafe_allow_html=True)
        st.write(f"👤 {st.session_state.user}")
        st.write(f"Rôle : **{st.session_state.role}**")
        st.divider()
        if st.button("Déconnexion"): 
            st.session_state.user = None
            st.rerun()

    # ==========================================
    # INTERFACE EMPLOYER (RECRUTEUR)
    # ==========================================
    if st.session_state.role == "Employeur":
        tab_pub, tab_sourc, tab_set = st.tabs(["📢 Diffuser une Offre", "📥 Sourcing & Filtrage", "⚙️ Mes Comptes"])

        with tab_pub:
            st.subheader("1. Fiche Métier & Assistant IA")
            col1, col2 = st.columns(2)
            with col1:
                titre = st.text_input("Intitulé du poste")
                contrat = st.selectbox("Contrat", ["CDI", "CDD", "Intérim", "Apprentissage"])
                lieu_job = st.text_input("Lieu (Ville / Pays)")
            with col2:
                salaire = st.text_input("Rémunération")
                xp = st.selectbox("Expérience", ["Débutant", "1-3 ans", "3-5 ans", "+5 ans"])
                langs = st.multiselect("Langues (20 disponibles)", LISTE_LANGUES)
            
            notes = st.text_area("Missions et avantages (pour l'IA)")
            if st.button("Rédiger l'annonce avec l'IA 🪄"):
                st.session_state.job_txt = f"OFFRE : {titre}\nLIEU : {lieu_job}\nLANGUES : {', '.join(langs)}\n\n{notes}"
            
            final_job = st.text_area("Annonce finalisée", value=st.session_state.get('job_txt', ""), height=150)
            st.download_button("📥 Télécharger PDF", data=final_job, file_name=f"offre_{titre}.txt")

            st.divider()
            st.subheader("2. Multipostage en 1 clic")
            pays_diff = st.multiselect("Pays de diffusion", list(DIFFUSEURS.keys()), default=["France 🇫🇷"])
            if pays_diff:
                cols = st.columns(len(pays_diff) + 1)
                for i, p in enumerate(pays_diff):
                    with cols[i]:
                        st.write(f"**{p}**")
                        for s, status in DIFFUSEURS[p].items():
                            st.checkbox(s, key=f"s_{p}_{s}")
                            st.markdown(f"<span class='{'tag-free' if status=='Inclus' else 'tag-account'}'>{status.upper()}</span>", unsafe_allow_html=True)
                with cols[-1]:
                    st.write("**Mes Agences**")
                    st.checkbox("Agence Intérim 1", value=True)
                    st.checkbox("Agence Intérim 2")

            if st.button("Lancer la Diffusion Mondiale 🚀"):
                st.success("Annonce envoyée aux diffuseurs sélectionnés !")

        with tab_sourc:
            st.subheader("🎨 Guide de lecture Zipngo")
            st.markdown("""<div class="legend-box">
                <div class="legend-item"><span class="dot" style="background-color: #1976d2;"></span> <b>Bleu :</b> Extérieur</div>
                <div class="legend-item"><span class="dot" style="background-color: #7b1fa2;"></span> <b>Violet :</b> Base Zipngo</div>
                <div class="legend-item"><span class="dot" style="background-color: #2e7d32;"></span> <b>Vert :</b> Top Match</div>
                <div class="legend-item"><span class="dot" style="background-color: #F3812B;"></span> <b>Orange :</b> 2ème Chance</div>
            </div>""", unsafe_allow_html=True)

            c_ext, c_zip = st.columns(2)
            with c_ext:
                st.markdown("### 📬 Candidatures Directes (Email)")
                st.markdown("<div class='bannette-card border-top'><span class='source-tag-ext'>EXT</span> <b>Jean D.</b> (94%)<br><small>✅ Critères ok</small></div>", unsafe_allow_html=True)
                st.markdown("<div class='bannette-card border-chance'><span class='source-tag-ext'>EXT</span> <b>Marc L.</b> (62%)<br><small>⚠️ À former</small></div>", unsafe_allow_html=True)
            with c_zip:
                st.markdown("### 🔍 Suggestions Base Zipngo")
                st.markdown("<div class='bannette-card border-top'><span class='source-tag-zip'>ZIP</span> <b>Profil #9921</b> (91%)<br><small>🎯 Localisation proche</small></div>", unsafe_allow_html=True)
                st.markdown("<div class='bannette-card border-chance'><span class='source-tag-zip'>ZIP</span> <b>Profil #4410</b> (Approchant)<br><small>✨ Soft-skills élevés</small></div>", unsafe_allow_html=True)

        with tab_set:
            st.subheader("⚙️ Configuration des accès")
            for i in range(1, 4):
                with st.expander(f"🏢 Agence d'Intérim {i}"):
                    st.text_input(f"Nom Agence {i}", key=f"an_{i}")
                    st.text_input(f"Login/Email {i}", key=f"al_{i}")
            with st.expander("🌐 Comptes Externes (LinkedIn, etc.)"):
                st.text_input("Identifiant Global")
                st.text_input("Mot de passe Global", type="password")

    # ==========================================
    # INTERFACE CANDIDATE (CANDIDAT)
    # ==========================================
    elif st.session_state.role == "Candidat":
        t_ia, t_vid, t_jobs = st.tabs(["🪄 Coach IA & CV", "🎥 Vidéo Pitch", "💼 Mes Candidatures"])

        with t_ia:
            st.subheader("Analyse & Relooking de CV")
            st.markdown('<div class="instruction-note">Collez votre CV pour que l\'IA l\'optimise selon les standards mondiaux.</div>', unsafe_allow_html=True)
            cv_area = st.text_area("Votre CV actuel", height=200)
            if st.button("Améliorer mon CV ✨"):
                st.success("Analyse terminée ! Voici les points à corriger pour passer en 'Top Match'.")
                st.write("- Détaillez vos certifications et langues.")

        with t_vid
