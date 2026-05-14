import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx", layout="wide")

LANGUAGES = ["Français", "English (US)", "Malagasy", "Español", "Deutsch"]

def apply_zip_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 2px solid #00E5FF; }
        /* Boutons Bleu Marine */
        .stButton>button { 
            background: #1A237E !important; color: #00E5FF !important; 
            border-radius: 25px; border: 2px solid #00E5FF; font-weight: bold; width: 100%; 
        }
        .footer-zip { text-align: center; padding: 20px; margin-top: 50px; font-weight: 300; color: #94a3b8; }
        .legal-link-zip { color: #94a3b8; text-decoration: none; font-size: 11px; margin: 0 10px; font-weight: 300; }
        .legal-content { font-size: 10px; line-height: 1.4; text-align: justify; font-weight: 300; display: none; margin-top: 10px; }
        #mentions_z:target, #cgv_z:target { display: block; padding: 15px; border: 1px solid #e2e8f0; border-radius: 5px; }
        .orange-thumb { color: #FF9800; font-size: 50px; text-align: center; margin-bottom: 10px; }
        .mail-icon { font-size: 18px; text-decoration: none !important; vertical-align: middle; }
        .ats-panel { padding: 15px; border-radius: 10px; background: #E3F2FD; border-left: 5px solid #00E5FF; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

if "z_auth" not in st.session_state: st.session_state.z_auth = False

apply_zip_theme()

if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.selectbox("Langue / Language", LANGUAGES, key="lang_zip")
        st.markdown('<div class="orange-thumb">👍</div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#1A237E; font-size: 48px; margin-top:-20px;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        
        st.text_input("Identifiant")
        st.text_input("Mot de passe", type="password")
        if st.button("DÉCOLLER"): 
            st.session_state.z_auth = True
            st.rerun()
else:
    with st.sidebar:
        st.title("zipngo.zaxx")
        st.markdown('<span style="font-size:30px;">👍</span>', unsafe_allow_html=True)
        menu = st.radio("Navigation", ["🌍 Dispatch Offres", "📄 Relooking & ATS", "📹 Entretien", "⚙️ Profil"])
        if st.button("Déconnexion"): st.session_state.z_auth = False; st.rerun()

    if menu == "🌍 Dispatch Offres":
        st.header("Opportunités Internationales")
        st.table(pd.DataFrame({'Poste': ['Fullstack Dev', 'Marketing'], 'Lieu': ['Remote', 'Europe']}))
    elif menu == "📄 Relooking & ATS":
        st.header("Optimisation CV")
        f = st.file_uploader("CV (PDF)", type=["pdf"])
        if f:
            st.markdown('<div class="ats-panel">⚠️ **Score ATS : 42/100**</div>', unsafe_allow_html=True)
            if st.button("✨ RELOOKER MON CV"):
                st.success("Optimisé !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9; border-color:#2E7D32;">✅ **Score ATS : 98/100**</div>', unsafe_allow_html=True)
    elif menu == "📹 Entretien":
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# PIED DE PAGE ZIPNGO
st.markdown("""
<div class="footer-zip">
    <a href="#mentions_z" class="legal-link-zip">Mentions Légales</a> | 
    <a href="#cgv_z" class="legal-link-zip">CGV</a>
    <div id="mentions_z" class="legal-content">
        <b>Mentions Légales :</b> zipngo.zaxx est édité par Liliane RAKOTOBE. 
        Les informations recueillies font l’objet d’un traitement destiné à la mise en relation professionnelle.
    </div>
    <div id="cgv_z" class="legal-content">
        <b>CGV :</b> Les données personnelles sont supprimées sur simple demande par mail. 
        <b>Mise en veille :</b> En cas d'absence d'activité pendant 90 jours, le profil utilisateur sera automatiquement mis en veille. 
    </div>
    <p style="font-size:12px; margin-top:15px; font-weight: 400;">© 2026 zipngo.zaxx | Créatrice : Liliane RAKOTOBE 
    <a href="mailto:creationsites06@gmail.com" class="mail-icon">✉️</a></p>
</div>
""", unsafe_allow_html=True)
