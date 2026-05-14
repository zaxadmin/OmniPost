import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Recruitment & ATS", layout="wide")

LANGUAGES = [
    "Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", 
    "Português", "Русский", "中文", "日本語", "한국어", "العربية", "हिन्दी", 
    "Türkçe", "Nederlands", "Polski", "Svenska", "Tiếng Việt", "Ελληνικά", "Português (BR)"
]

def apply_zip_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 2px solid #00E5FF; }
        .stButton>button { background: #1A237E !important; color: #00E5FF !important; border-radius: 25px; border: 2px solid #00E5FF; font-weight: bold; width: 100%; }
        .footer-zip { position: fixed; left: 0; bottom: 0; width: 100%; background: #1A237E; color: white; text-align: center; padding: 15px; font-size: 11px; z-index: 999; }
        .ats-panel { padding: 20px; border-radius: 15px; background: #E3F2FD; border: 1px solid #00E5FF; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if "z_auth" not in st.session_state: st.session_state.z_auth = False

apply_zip_theme()

if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        st.selectbox("Langue / Language", LANGUAGES)
        st.text_input("Identifiant", key="z_mail")
        st.text_input("Mot de passe", type="password", key="z_pass")
        if st.button("DÉCOLLER"): st.session_state.z_auth = True; st.rerun()
    st.markdown('<div class="footer-zip">zipngo.zaxx | Recrutement Global | © 2026</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        st.title("zipngo.zaxx")
        menu = st.selectbox("Menu Principal", ["🌍 Dispatch Offres", "📄 Relooking CV & ATS", "📹 Entretien Vidéo", "⚙️ Profil"])
        if st.button("Quitter"): st.session_state.z_auth = False; st.rerun()

    if menu == "🌍 Dispatch Offres":
        st.header("Offres d'Emploi Mondiales")
        c1, c2 = st.columns(2)
        pays = c1.selectbox("Filtrer par pays", ["Madagascar", "France", "USA", "Monde Entier"])
        remote = c2.checkbox("Remote / Télétravail uniquement")
        st.info(f"Recherche : {pays} | Remote : {remote}")
        st.table(pd.DataFrame({'Poste': ['Software Eng', 'Lead Sales'], 'Lieu': [pays, 'Remote'], 'Contrat': ['CDI', 'Freelance']}))

    elif menu == "📄 Relooking CV & ATS":
        st.header("Service Relooking & Scoring ATS")
        st.write("Optimisez votre CV pour les algorithmes de recrutement mondiaux.")
        
        cv_file = st.file_uploader("Uploader votre CV (PDF)", type=["pdf"])
        if cv_file:
            st.markdown('<div class="ats-panel">⚠️ **Premier test ATS : 41/100** <br> Analyse : Structure non reconnue par les systèmes RH standards.</div>', unsafe_allow_html=True)
            
            if st.button("✨ LANCER LE RELOOKING IA"):
                st.success("Relooking terminé avec succès !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9;">✅ **Second test ATS (Après Relooking) : 98/100** <br> Analyse : CV parfaitement optimisé pour le dispatch mondial.</div>', unsafe_allow_html=True)
                st.download_button("📥 Télécharger mon CV Relooké", "Contenu_CV_Relooke", "CV_Elite_Zipngo.pdf")

    elif menu == "📹 Entretien Vidéo":
        st.header("Préparation aux Entretiens")
        st.write("Découvrez comment réussir vos entretiens vidéo pour des postes internationaux.")
        st.markdown('<div style="border: 2px solid #1A237E; border-radius: 12px; overflow: hidden;">', unsafe_allow_html=True)
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("Tutoriel : Maîtriser son image et son discours en vidéo.")

    st.markdown('<div class="footer-zip">zipngo.zaxx | Direction : Liliane RAKOTOBE | ZAXX Group</div>', unsafe_allow_html=True)
