import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Recruitment & ATS", layout="wide")

LANGUAGES = [
    "Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", 
    "Português", "Русский", "中文", "日本語", "한국어", "العربية", "हिन्दी", 
    "Türkçe", "Nederlands", "Polski", "Svenska", "Tiếng Việt", "Ελληνικά", "Português (BR)"
]

def render_zipngo_logo(height=180):
    """Affiche le logo graphique inspiré de logo-zipngo.jpg"""
    logo_html = f"""
    <div style="background-color: #1A237E; padding: 20px; text-align: center; border-radius: 15px; font-family: 'Arial Black', sans-serif; margin-bottom: 20px;">
        <div style="display: flex; align-items: baseline; justify-content: center;">
            <span style="color: white; font-size: 55px; letter-spacing: -3px;">zipngo</span>
            <span style="color: #00e5ff; font-size: 45px; margin: 0 5px;">.</span>
            <div style="background: #ff8c00; padding: 2px 12px; border-radius: 8px; position: relative; margin-left: 5px;">
                <span style="color: #00e5ff; font-size: 45px; font-weight: 900;">zaxx</span>
                <span style="position: absolute; top: -32px; right: -5px; font-size: 35px;">👍</span>
            </div>
        </div>
        <hr style="height: 2px; background: white; border: none; margin: 10px 0;">
        <div style="color: white; font-family: Arial; font-size: 16px; letter-spacing: 7px; text-transform: uppercase;">
            The power of choice
        </div>
    </div>
    """
    st.components.v1.html(logo_html, height=height)

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

# Initialisation des états
if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"
if "z_email" not in st.session_state: st.session_state.z_email = "candidat@zipngo.com"

apply_zip_theme()

if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        # LOGO GRAPHIQUE ICI
        render_zipngo_logo(height=180)
        
        if st.session_state.z_view == "login":
            st.selectbox("Langue / Language", LANGUAGES)
            st.text_input("Identifiant", key="z_u")
            st.text_input("Mot de passe", type="password", key="z_p")
            if st.button("DÉCOLLER"): 
                st.session_state.z_auth = True
                st.rerun()
            st.button("Mot de passe oublié ?", key="z_forgot", on_click=lambda: st.session_state.update({"z_view": "forgot"}))
        
        elif st.session_state.z_view == "forgot":
            st.subheader("Récupération de compte")
            st.text_input("Email enregistré")
            if st.button("Récupérer mes accès"): 
                st.info("Un email de récupération vous a été envoyé.")
            st.button("Retour à la connexion", on_click=lambda: st.session_state.update({"z_view": "login"}))
            
    st.markdown('<div class="footer-zip">zipngo.zaxx | Recrutement Global | © 2026</div>', unsafe_allow_html=True)
else:
    with st.sidebar:
        # LOGO GRAPHIQUE DANS LA SIDEBAR
        render_zipngo_logo(height=160)
        menu = st.selectbox("Menu Principal", ["🌍 Dispatch Offres", "📄 Relooking CV & ATS", "📹 Entretien Vidéo", "⚙️ Espace Personnel"])
        if st.button("🚪 Quitter"): st.session_state.z_auth = False; st.rerun()

    if menu == "🌍 Dispatch Offres":
        st.header("Opportunités de Carrière")
        c1, c2 = st.columns(2)
        pays = c1.selectbox("Filtrer par Pays", ["Madagascar", "France", "USA", "Monde Entier"])
        remote = c2.checkbox("Remote / Télétravail uniquement")
        st.info(f"Recherche : {pays} | Remote : {remote}")
        st.table(pd.DataFrame({'Poste': ['Chef de Projet', 'Développeur Python'], 'Lieu': [pays, 'Remote']}))

    elif menu == "📄 Relooking CV & ATS":
        st.header("Relooking CV & Scoring ATS")
        st.write("Uploadez votre CV pour maximiser vos chances.")
        f = st.file_uploader("Déposer CV (PDF)", type=["pdf"])
        if f:
            st.markdown('<div class="ats-panel">📊 **Score ATS Initial : 39/100** <br> Analyse : Structure incompatible avec les robots recruteurs.</div>', unsafe_allow_html=True)
            if st.button("✨ LANCER LE RELOOKING IA"):
                st.success("Relooking terminé !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9;">✅ **Nouveau Score ATS : 97/100** <br> Analyse : Parfaitement optimisé pour le dispatch mondial.</div>', unsafe_allow_html=True)
                st.download_button("📥 Télécharger mon CV Relooké", "Contenu_du_CV", "CV_Elite_Zipngo.pdf")

    elif menu == "📹 Entretien Vidéo":
        st.header("Préparation Entretien")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        st.info("Coaching : Comment réussir son entretien vidéo pour un poste à l'international.")

    elif menu == "⚙️ Espace Personnel":
        st.header("Mon Profil Candidat")
        new_z_email = st.text_input("Changer mon adresse email", value=st.session_state.z_email)
        if st.button("Mettre à jour l'email"):
            st.session_state.z_email = new_z_email
            st.toast("Email mis à jour avec succès !")
        st.text_input("Changer le mot de passe", type="password")
        st.button("Enregistrer les modifications")

    st.markdown('<div class="footer-zip">zipngo.zaxx | Direction : Liliane RAKOTOBE | ZAXX Group</div>', unsafe_allow_html=True)
