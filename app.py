import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Recruitment", layout="wide")

T = {
    "Français": {
        "intro": "La plateforme de dispatch mondial d'offres d'emploi et de relooking CV optimisé ATS.",
        "desc": "zipngo.zaxx propulse votre carrière à l'international grâce à notre technologie d'analyse de CV et nos outils de coaching vidéo.",
        "user": "Identifiant Candidat", "pw": "Mot de passe", "login": "VALIDER",
        "create": "CRÉER MON COMPTE", "forgot": "Mot de passe oublié ?", "signup_t": "Rejoindre l'aventure zipngo",
        "name": "Prénom & Nom", "email": "Email", "submit": "VALIDER MON INSCRIPTION", "back": "Retour"
    },
    "English (US)": {
        "intro": "The global job dispatch platform and ATS-optimized CV makeover service.",
        "desc": "zipngo.zaxx boosts your international career with our CV analysis technology and video coaching tools.",
        "user": "Candidate ID", "pw": "Password", "login": "VALIDATE",
        "create": "CREATE ACCOUNT", "forgot": "Forgot password?", "signup_t": "Join the zipngo adventure",
        "name": "Full Name", "email": "Email", "submit": "VALIDATE REGISTRATION", "back": "Back"
    },
    "Malagasy": {
        "intro": "Fandefasana tolotra asa manerantany sy fanamboarana CV ho matihanina.",
        "desc": "zipngo.zaxx dia manampy anao hahita asa any ivelany amin'ny alalan'ny teknolojia vaovao.",
        "user": "Anarana", "pw": "Teny miafina", "login": "TSARA",
        "create": "HANOKATRA KAONTY", "forgot": "Adino ny teny miafina?", "signup_t": "Fidirana ato amin'ny zipngo",
        "name": "Anarana feno", "email": "Email", "submit": "ALFAY NY FISORATANA", "back": "Hiverina"
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
        #mentions_z:target, #cgv_z:target { display: block; padding: 15px; border: 1px solid #e2e8f0; }
        .orange-thumb { color: #FF9800; font-size: 50px; text-align: center; margin-bottom: 10px; }
        .mail-icon { font-size: 18px; text-decoration: none !important; vertical-align: middle; }
        .ats-panel { padding: 15px; border-radius: 10px; background: #E3F2FD; border-left: 5px solid #00E5FF; margin: 10px 0; }
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
        st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1A237E;'>{text['intro']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size:14px;'>{text['desc']}</p>", unsafe_allow_html=True)
        
        if st.session_state.z_view == "login":
            st.text_input(text["user"])
            st.text_input(text["pw"], type="password")
            if st.button(text["login"]): st.session_state.z_auth = True; st.rerun()
            if st.button(text["create"]): st.session_state.z_view = "signup"; st.rerun()
            st.button(text["forgot"], on_click=lambda: st.session_state.update({"z_view": "forgot"}))
        
        elif st.session_state.z_view == "signup":
            st.subheader(text["signup_t"])
            st.text_input(text["name"])
            st.text_input(text["email"])
            if st.button(text["submit"]): st.success("Compte créé avec succès."); st.session_state.z_view = "login"; st.rerun()
            st.button(text["back"], on_click=lambda: st.session_state.update({"z_view": "login"}))
else:
    with st.sidebar:
        st.title("zipngo.zaxx")
        menu = st.sidebar.radio("Navigation", ["🌍 Dispatch Offres", "📄 Relooking & ATS", "📹 Entretien", "⚙️ Profil"])
        if st.sidebar.button("Déconnexion"): st.session_state.z_auth = False; st.rerun()
    
    if menu == "📄 Relooking & ATS":
        st.header("Optimisation CV & Score ATS")
        f = st.file_uploader("Uploadez votre CV (PDF)", type=["pdf"])
        if f:
            st.markdown('<div class="ats-panel">⚠️ **Score ATS actuel : 42/100**</div>', unsafe_allow_html=True)
            if st.button("✨ RELOOKER MON CV"):
                st.success("Optimisation terminée !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9; border-color:#2E7D32;">✅ **Nouveau Score ATS : 98/100**</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footer-zip">
    <a href="#mentions_z" class="legal-link-zip">Mentions Légales</a> | <a href="#cgv_z" class="legal-link-zip">CGV</a>
    <div id="mentions_z" class="legal-content"><b>Mentions :</b> Édité par Liliane RAKOTOBE. Suppression des données sur simple demande par mail.</div>
    <div id="cgv_z" class="legal-content"><b>CGV :</b> Mise en veille automatique après 90 jours sans activité.</div>
    <p>© 2026 zipngo.zaxx | Créatrice : Liliane RAKOTOBE <a href="mailto:creationsites06@gmail.com" class="mail-icon">✉️</a></p>
</div>
""", unsafe_allow_html=True)
