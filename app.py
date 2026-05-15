import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx", layout="wide")

# Dictionnaire de traduction
T = {
    "Français": {
        "user": "Identifiant", "pw": "Mot de passe", "login": "VALIDER",
        "create": "CRÉER MON COMPTE", "forgot": "Mot de passe oublié ?", "signup_t": "Rejoindre l'aventure",
        "name": "Prénom & Nom", "submit": "VALIDER MON INSCRIPTION", "back": "Retour"
    },
    "English (US)": {
        "user": "Username", "pw": "Password", "login": "VALIDATE",
        "create": "CREATE ACCOUNT", "forgot": "Forgot password?", "signup_t": "Join the adventure",
        "name": "Full Name", "submit": "VALIDATE MY REGISTRATION", "back": "Back"
    },
    "Malagasy": {
        "user": "Anarana", "pw": "Teny miafina", "login": "TSARA",
        "create": "HANOKATRA KAONTY", "forgot": "Adino ny teny miafina?", "signup_t": "Fidirana",
        "name": "Anarana feno", "submit": "ALFAY NY FISORATANA", "back": "Hiverina"
    }
}

def apply_zip_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 2px solid #00E5FF; }
        .stButton>button { 
            background: #1A237E !important; color: #00E5FF !important; 
            border-radius: 25px; border: 2px solid #00E5FF; font-weight: bold; width: 100%; 
        }
        .footer-zip { text-align: center; padding: 20px; margin-top: 50px; font-weight: 300; color: #94a3b8; }
        .legal-link-zip { color: #94a3b8; text-decoration: none; font-size: 11px; margin: 0 10px; }
        .legal-content { font-size: 10px; line-height: 1.4; text-align: justify; font-weight: 300; display: none; margin-top: 10px; }
        #mentions_z:target, #cgv_z:target { display: block; padding: 15px; border: 1px solid #e2e8f0; border-radius: 5px; }
        .orange-thumb { color: #FF9800; font-size: 50px; text-align: center; margin-bottom: 10px; }
        .mail-icon { font-size: 18px; text-decoration: none !important; vertical-align: middle; }
    </style>
    """, unsafe_allow_html=True)

if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"

apply_zip_theme()

if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        lang = st.selectbox("Langue / Language", list(T.keys()), key="lang_zip")
        text = T[lang]
        st.markdown('<div class="orange-thumb">👍</div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#1A237E; font-size: 48px; margin-top:-20px;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        
        if st.session_state.z_view == "login":
            st.text_input(text["user"])
            st.text_input(text["pw"], type="password")
            if st.button(text["login"]): st.session_state.z_auth = True; st.rerun()
            if st.button(text["create"]): st.session_state.z_view = "signup"; st.rerun()
            st.button(text["forgot"], on_click=lambda: st.session_state.update({"z_view": "forgot"}))
        
        elif st.session_state.z_view == "signup":
            st.subheader(text["signup_t"])
            st.text_input(text["name"])
            st.text_input("Email")
            if st.button(text["submit"]): st.success("OK"); st.rerun()
            st.button(text["back"], on_click=lambda: st.session_state.update({"z_view": "login"}))
else:
    st.sidebar.title("zipngo.zaxx")
    if st.sidebar.button("Déconnexion"): st.session_state.z_auth = False; st.rerun()
    st.header("Opportunités")
    st.table(pd.DataFrame({'Poste': ['Dev', 'Marketing'], 'Lieu': ['Remote', 'Europe']}))

st.markdown("""
<div class="footer-zip">
    <a href="#mentions_z" class="legal-link-zip">Mentions Légales</a> | <a href="#cgv_z" class="legal-link-zip">CGV</a>
    <div id="mentions_z" class="legal-content"><b>Mentions :</b> zipngo.zaxx par Liliane RAKOTOBE. Suppression sur simple demande.</div>
    <div id="cgv_z" class="legal-content"><b>CGV :</b> Mise en veille auto après 90 jours sans activité.</div>
    <p>© 2026 zipngo.zaxx | Créatrice : Liliane RAKOTOBE <a href="mailto:creationsites06@gmail.com" class="mail-icon">✉️</a></p>
</div>
""", unsafe_allow_html=True)
