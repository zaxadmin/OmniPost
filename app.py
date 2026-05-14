import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Global Recruitment", layout="wide")

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
        a { color: #00E5FF !important; text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"
if "z_email" not in st.session_state: st.session_state.z_email = "candidat@zipngo.com"

apply_zip_theme()

# FOOTER REUSABLE
footer_zip_html = '<div class="footer-zip">zipngo.zaxx | <a href="#">CGV</a> | <a href="#">Mentions Légales</a> | Créatrice : Liliane RAKOTOBE</div>'

if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        
        if st.session_state.z_view == "login":
            st.selectbox("Langue de navigation", LANGUAGES)
            st.text_input("Identifiant Candidat / Recruteur", key="z_u")
            st.text_input("Mot de passe", type="password", key="z_p")
            
            if st.button("DÉCOLLER"): 
                st.session_state.z_auth = True
                st.rerun()
            
            st.button("Accès perdu ?", on_click=lambda: st.session_state.update({"z_view": "forgot"}))
        
        elif st.session_state.z_view == "forgot":
            st.subheader("Récupération de compte")
            st.text_input("Email associé à votre compte zipngo")
            if st.button("Récupérer ma clé d'accès"): 
                st.info("Un email de secours a été envoyé.")
            st.button("Retour à la connexion", on_click=lambda: st.session_state.update({"z_view": "login"}))
            
    st.markdown(footer_zip_html, unsafe_allow_html=True)
else:
    with st.sidebar:
        st.title("zipngo.zaxx")
        menu = st.selectbox("Modules", ["🌍 Dispatch Offres", "📄 Relooking & ATS", "📹 Entretien Vidéo", "⚙️ Mon Profil"])
        if st.button("Déconnexion"): st.session_state.z_auth = False; st.rerun()

    if menu == "🌍 Dispatch Offres":
        st.header("Opportunités Internationales")
        c1, c2 = st.columns(2)
        pays = c1.selectbox("Pays cible", ["Madagascar", "France", "USA", "Monde Entier"])
        remote = c2.checkbox("Remote / Télétravail uniquement")
        st.table(pd.DataFrame({'Poste': ['Chef de Projet IT', 'Analyste Business'], 'Lieu': [pays, 'Télétravail']}))
        
    elif menu == "📄 Relooking & ATS":
        st.header("Optimisation de Candidature (ATS)")
        st.write("Téléchargez votre CV pour le test de compatibilité.")
        f = st.file_uploader("Fichier CV (PDF)", type=["pdf"])
        if f:
            st.markdown('<div class="ats-panel">⚠️ **Premier test ATS : 38/100** <br> Diagnostic : Mots-clés manquants.</div>', unsafe_allow_html=True)
            if st.button("✨ RELOOKER MON CV"):
                st.success("Optimisation IA terminée !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9; border-color:#2E7D32; color:#1B5E20;">✅ **Second test ATS : 97/100** <br> Votre CV est prêt.</div>', unsafe_allow_html=True)
                st.download_button("📥 Télécharger le CV Optimisé", "DATA_PRO", "CV_Zipngo_Pro.pdf")
            
    elif menu == "📹 Entretien Vidéo":
        st.header("Préparation Entretien")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        
    elif menu == "⚙️ Mon Profil":
        st.header("Paramètres personnels")
        st.session_state.z_email = st.text_input("Modifier l'email", value=st.session_state.z_email)
        if st.button("Enregistrer"): st.toast("Email mis à jour !")
        st.text_input("Nouveau mot de passe", type="password")

    st.markdown(footer_zip_html, unsafe_allow_html=True)
