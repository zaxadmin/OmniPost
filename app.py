import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Recruitment", layout="wide")

LANGUAGES = ["Français", "English (US)", "Malagasy", "Español", "Deutsch"]

def apply_zip_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 2px solid #00E5FF; }
        /* Tous les boutons en Bleu Marine */
        .stButton>button { 
            background: #1A237E !important; 
            color: #00E5FF !important; 
            border-radius: 25px; 
            border: 2px solid #00E5FF; 
            font-weight: bold; 
            width: 100%; 
        }
        .footer-zip { text-align: center; padding: 30px; font-size: 12px; background: #f8fafc; border-top: 2px solid #1A237E; margin-top: 50px; }
        .legal-box-zip { text-align: left; border: 1px solid #cbd5e1; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #334155; }
        .ats-panel { padding: 15px; border-radius: 10px; background: #E3F2FD; border-left: 5px solid #00E5FF; margin: 10px 0; }
        .orange-thumb { color: #FF9800; font-size: 50px; text-align: center; margin-bottom: 10px; }
        a { color: #1A237E; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if "z_auth" not in st.session_state: st.session_state.z_auth = False

apply_zip_theme()

if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        # 1. Langues en haut
        st.selectbox("Choisir la langue / Select Language", LANGUAGES, key="lang_zip")
        
        # 2. Pouce Orange et Titre
        st.markdown('<div class="orange-thumb">👍</div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#1A237E; font-size: 48px; margin-top:-20px;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        
        st.text_input("Identifiant Candidat")
        st.text_input("Mot de passe", type="password")
        if st.button("DÉCOLLER"): 
            st.session_state.z_auth = True
            st.rerun()
        st.button("Accès perdu ?")
else:
    with st.sidebar:
        st.title("zipngo.zaxx")
        st.markdown('<span style="font-size:30px;">👍</span>', unsafe_allow_html=True)
        menu = st.radio("Navigation", ["🌍 Dispatch Offres", "📄 Relooking & ATS", "📹 Entretien Vidéo", "⚙️ Mon Profil"])
        if st.button("Déconnexion"): st.session_state.z_auth = False; st.rerun()

    if menu == "🌍 Dispatch Offres":
        st.header("Opportunités de carrière internationales")
        pays = st.selectbox("Destination cible", ["Madagascar", "France", "Canada", "Remote"])
        st.table(pd.DataFrame({
            'Poste': ['Développeur Fullstack', 'Data Analyst', 'Project Manager'],
            'Société': ['Global Tech', 'Innova Sarl', 'Zaxx-Corp'],
            'Lieu': [pays, pays, pays]
        }))
        
    elif menu == "📄 Relooking & ATS":
        st.header("Analyseur de CV & Score ATS")
        f = st.file_uploader("Uploadez votre CV (PDF)", type=["pdf"])
        if f:
            st.markdown('<div class="ats-panel">⚠️ **Premier test ATS : 42/100**<br>Diagnostic : Structure incompatible.</div>', unsafe_allow_html=True)
            if st.button("✨ RELOOKER MON CV MAINTENANT"):
                st.success("Refonte IA terminée !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9; border-color:#2E7D32;">✅ **Second test ATS : 98/100**<br>Votre CV est prêt pour le dispatch.</div>', unsafe_allow_html=True)
                st.download_button("📥 Télécharger le CV Optimisé", "DATA", "CV_PRO_ZIPNGO.pdf")
                
    elif menu == "📹 Entretien Vidéo":
        st.header("Coaching Vidéo")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# FOOTER JURIDIQUE
st.markdown("""
<div class="footer-zip">
    <div class="legal-box-zip">
        <b>Mentions Légales :</b> zipngo.zaxx est une plateforme opérée par <b>ZAXX Group</b>. 
        Siège social à Antananarivo. Directrice de publication : Liliane RAKOTOBE. 
        Conformément à la RGPD, vous disposez d'un droit d'accès à vos données.
    </div>
    <div class="legal-box-zip">
        <b>CGV :</b> zipngo.zaxx agit en tant que facilitateur. ZAXX Group ne garantit pas l'embauche. 
        Le service de relooking est une aide technique à l'optimisation de profil.
    </div>
    <p>© 2026 zipngo.zaxx | Créatrice : <b>Liliane RAKOTOBE</b> 
    <a href="mailto:creationsites06@gmail.com">✉️ creationsites06@gmail.com</a></p>
</div>
""", unsafe_allow_html=True)
