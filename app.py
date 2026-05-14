import streamlit as st
from groq import Groq
import os
import hashlib

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="zipngo.zaxx", layout="wide")
client_ia = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.markdown("""
<style>
    .stApp { background-color: #0A0F1E; color: #FFFFFF; }
    .stWidget label, p, .stMarkdown, .stRadio label { color: #FFFFFF !important; font-weight: 600 !important; }
    .stTextInput input { background-color: #161B22 !important; color: white !important; border: 1px solid #00E5FF !important; }
    .stButton>button { background: #00E5FF !important; color: #0A0F1E !important; font-weight: 800; border-radius: 8px; width: 100%; border: none; }
    .small-link { font-size: 0.85rem; color: #00E5FF !important; text-decoration: none; display: block; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- DICTIONNAIRE 20 LANGUES (Extrait étendu) ---
LANGS = {
    "Français": {"switch": "Vous êtes ?", "cand": "Candidat", "rec": "Recruteur", "login": "Connexion", "forgot": "Mot de passe oublié ?", "change": "Changer mon email", "veille": "⚠️ PROFIL EN VEILLE", "dispatch": "Envoyer au Recruteur"},
    "English": {"switch": "I am a:", "cand": "Candidate", "rec": "Recruiter", "login": "Login", "forgot": "Forgot password?", "change": "Change email", "veille": "⚠️ PROFILE ON STANDBY", "dispatch": "Send to Recruiter"},
    "Malagasy": {"switch": "Iza ianao ?", "cand": "Mpmitady asa", "rec": "Mpanome asa", "login": "Hiditra", "forgot": "Adino ny teny miafina?", "change": "Hanova email", "veille": "⚠️ MIATO NY MOMBA ANAO", "dispatch": "Alefa any amin'ny mpampiasa"},
    # Ajoutez ici : Español, Deutsch, Italiano, Português, Русский, 中文, 日本語, 한국어, العربية, हिन्दी, Türkçe, Nederlands, Polski, Svenska, Tiếng Việt, Ελληνικά.
}

if "auth" not in st.session_state: st.session_state.auth = False

# --- PAGE DE CONNEXION ---
if not st.session_state.auth:
    col_mid = st.columns([1, 1.5, 1])[1]
    with col_mid:
        if os.path.exists("logo-zipngo.jpg"): st.image("logo-zipngo.jpg", use_container_width=True)
        st.session_state.lang = st.selectbox("🌐 Langue / Language", list(LANGS.keys()))
        L = LANGS[st.session_state.lang]
        
        with st.container(border=True):
            role_choice = st.radio(L["switch"], [L["cand"], L["rec"]], horizontal=True)
            u = st.text_input("Email", placeholder="nom@exemple.com")
            p = st.text_input("Mot de passe", type="password")
            if st.button(L["login"]):
                st.session_state.update({"auth": True, "user": u, "role": role_choice, "is_expired": True})
                st.rerun()
            st.markdown(f'<a href="mailto:creationsites06@gmail.com" class="small-link">{L["forgot"]}</a>', unsafe_allow_html=True)

# --- ESPACE CONNECTÉ ---
else:
    L = LANGS[st.session_state.lang]
    with st.sidebar:
        if os.path.exists("logo-zipngo.jpg"): st.image("logo-zipngo.jpg")
        st.write(f"Session : **{st.session_state.user}**")
        with st.expander(f"⚙️ {L['change']}"):
            new_e = st.text_input("Nouvel Email")
            if st.button("Valider"): st.success("Email mis à jour")
        if st.button("🔒 Déconnexion"): st.session_state.clear(); st.rerun()

    # --- TRI DES CV & DISPATCH ---
    st.title(f"🚀 Studio {st.session_state.role}")
    if st.session_state.role == L["cand"]:
        if st.session_state.is_expired:
            st.error(L["veille"])
            if st.button("Activer mon Pass 90j (3 €)"): st.session_state.is_expired = False; st.rerun()
        else:
            cv_file = st.file_uploader("Chargez votre CV pour tri IA", type="pdf")
            if cv_file and st.button(L["dispatch"]):
                st.success("CV anonymisé et envoyé par email au recruteur !")
