import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Talent Dispatch", layout="wide")

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
        a { color: #00E5FF !important; }
    </style>
    """, unsafe_allow_html=True)

if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"
if "z_email" not in st.session_state: st.session_state.z_email = "candidat@zipngo.com"

apply_zip_theme()

if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        
        if st.session_state.z_view == "login":
            st.selectbox("Choisir votre langue", LANGUAGES)
            st.text_input("Identifiant Candidat", key="z_u")
            st.text_input("Mot de passe", type="password", key="z_p")
            if st.button("DÉCOLLER"): 
                st.session_state.z_auth = True
                st.rerun()
            st.button("Mot de passe perdu ?", on_click=lambda: st.session_state.update({"z_view": "forgot"}))
        
        elif st.session_state.z_view == "forgot":
            st.subheader("Récupération de compte")
            st.text_input("Email enregistré")
            if st.button("Envoyer ma nouvelle clé"): st.info("Instructions envoyées par email.")
            st.button("Retour", on_click=lambda: st.session_state.update({"z_view": "login"}))
            
    st.markdown('<div class="footer-zip">zipngo.zaxx | <a href="#">CGV</a> | Recrutement Global | © 2026</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        st.title("zipngo.zaxx")
        menu = st.selectbox("Menu Principal", ["🌍 Dispatch Offres", "📄 Relooking CV & ATS", "📹 Entretien Vidéo", "⚙️ Espace Personnel"])
        if st.button("🚪 Déconnexion"): st.session_state.z_auth = False; st.rerun()

    if menu == "🌍 Dispatch Offres":
        st.header("Opportunités de Carrière")
        pays = st.selectbox("Filtrer par Pays", ["Madagascar", "France", "USA", "Monde Entier"])
        st.table(pd.DataFrame({'Poste': ['Chef de Projet', 'Expert IT'], 'Lieu': [pays, 'Remote']}))

    elif menu == "📄 Relooking CV & ATS":
        st.header("Service Relooking & Scoring ATS")
        f = st.file_uploader("Uploader votre CV (PDF)", type=["pdf"])
        if f:
            st.markdown('<div class="ats-panel">📊 **Score ATS Actuel : 37/100**</div>', unsafe_allow_html=True)
            if st.button("✨ RELOOKER MON CV"):
                st.success("Relooking terminé avec succès !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9;">✅ **Score ATS Après Relooking : 98/100**</div>', unsafe_allow_html=True)
                st.download_button("📥 Télécharger le CV Optimisé", "CV_PRO_DATA", "CV_Zipngo_Expert.pdf")

    elif menu == "📹 Entretien Vidéo":
        st.header("Préparation Entretien Vidéo")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        st.info("Conseils pour réussir votre pitch vidéo face aux recruteurs internationaux.")

    elif menu == "⚙️ Espace Personnel":
        st.header("Gestion du Profil")
        st.session_state.z_email = st.text_input("Changer mon email", value=st.session_state.z_email)
        if st.button("Sauvegarder l'email"): st.toast("Email mis à jour !")
        st.text_input("Nouveau mot de passe", type="password")
        st.button("Mettre à jour mon profil")

    st.markdown('<div class="footer-zip">zipngo.zaxx | <a href="#">CGV</a> | Direction : Liliane RAKOTOBE | ZAXX Group</div>', unsafe_allow_html=True)
