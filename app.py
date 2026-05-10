import streamlit as st
import pandas as pd
import streamlit_webrtc as webrtc
from PIL import Image
from streamlit_javascript import st_javascript
from processor import process_matching

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Zaxx.app | OmniPost IA", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    :root { --primary: #00467F; --cyan: #4FA9D1; --green: #22c55e; }
    .stButton>button { background-color: var(--primary); color: white; border-radius: 8px; width: 100%; }
    .buy-button { 
        display: inline-block; padding: 15px 30px; background-color: var(--green); 
        color: white !important; border-radius: 10px; text-decoration: none; 
        font-weight: bold; font-size: 18px; margin: 10px 0; text-align: center; width: 100%;
    }
    .license-alert { background-color: #fff5f5; border: 2px solid #ff4b4b; padding: 25px; border-radius: 12px; text-align: center; }
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background: white; text-align: center; padding: 15px; 
        border-top: 1px solid #ddd; z-index: 100; 
    }
    .score-box { padding: 20px; border-radius: 10px; border: 1px solid #ddd; background: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DÉTECTION IA LOCALE (BRIDGE JS) ---
# On récupère l'IP pour le quota et on vérifie si window.ai est dispo
user_ip = st_javascript("await fetch('https://api.ipify.org?format=json').then(res => res.json()).then(data => data.ip)")

has_local_ai = st_javascript("""
    async function check() {
        if (window.ai && (await window.ai.canCreateTextSession()) === "readily") {
            return true;
        }
        return false;
    }
    return await check();
""")

# --- 3. DONNÉES MULTILINGUES ---
LANG_DATA = {
    "Français 🇫🇷": {"region": "France", "welcome": "Bienvenue sur OmniPost"},
    "English (US) 🇺🇸": {"region": "Global/USA", "welcome": "Welcome to OmniPost"},
    "English (UK) 🇬🇧": {"region": "Global/UK", "welcome": "Welcome to OmniPost"},
    "Malagasy 🇲🇬": {"region": "Madagascar", "welcome": "Tongasoa eto amin'ny OmniPost"},
    "Deutsch 🇩🇪": {"region": "Germany", "welcome": "Willkommen bei OmniPost"},
    "Español 🇪🇸": {"region": "Spain", "welcome": "Bienvenido a OmniPost"},
    "Italiano 🇮🇹": {"region": "Global", "welcome": "Benvenuti in OmniPost"},
    "Português 🇧🇷": {"region": "Brazil", "welcome": "Bem-vindo ao OmniPost"},
    "Русский 🇷🇺": {"region": "Global", "welcome": "Добро пожаловать в OmniPost"},
    "日本語 🇯🇵": {"region": "Japan", "welcome": "OmniPostへようこそ"},
    "한국어 🇰🇷": {"region": "Global", "welcome": "OmniPost에 오신 것을 환영합니다"},
    "हिन्दी 🇮🇳": {"region": "Global", "welcome": "OmniPost में आपका स्वागत है"},
    "العربية 🇸🇦": {"region": "Global", "welcome": "مرحباً بكم في OmniPost"},
    "Türkçe 🇹🇷": {"region": "Global", "welcome": "OmniPost'a hoş geldiniz"},
    "Polski 🇵🇱": {"region": "Global", "welcome": "Witaj en OmniPost"},
    "Tiếng Việt 🇻🇳": {"region": "Global", "welcome": "Chào mừng đến với OmniPost"},
    "ไทย 🇹🇭": {"region": "Global", "welcome": "ยินดีต้อนรับสู่ OmniPost"},
    "Nederlands 🇳🇱": {"region": "Global", "welcome": "Welkom bij OmniPost"},
    "Bahasa Indonesia 🇮🇩": {"region": "Global", "welcome": "Selamat datang di OmniPost"},
    "Svenska 🇸🇪": {"region": "Global", "welcome": "Välkommen till OmniPost"}
}

DIFFUSEURS = {
    "France": ["France Travail", "Indeed", "APEC", "LinkedIn"],
    "Global/USA": ["Indeed (US)", "LinkedIn", "ZipRecruiter"],
    "Madagascar": ["Portal Job MG", "Orange Jobs", "LinkedIn"],
    "Global": ["LinkedIn", "Indeed (Global)", "Remote.com"]
}

# --- 4. GESTION DE L'ÉTAT ---
if 'ads_count' not in st.session_state: st.session_state.ads_count = 0

# --- 5. SIDEBAR ---
with st.sidebar:
    try:
        st.image('logo_omnipost.jpg', use_container_width=True)
    except:
        st.title("ZAXX.app")
    
    st.divider()
    selected_lang = st.selectbox("🌐 Langue / Language", list(LANG_DATA.keys()))
    region = LANG_DATA[selected_lang]["region"]
    
    if has_local_ai:
        st.success("🚀 IA Native détectée (Gratuit)")
    else:
        st.info("☁️ IA Cloud active")

# --- 6. DASHBOARD ---
st.title(LANG_DATA[selected_lang]["welcome"])

t1, t2, t3, t4 = st.tabs(["📢 Diffusion", "🔑 Comptes", "📂 Tri IA", "📈 Analytique"])

with t1:
    st.subheader("Publier une offre")
    title = st.text_input("Titre du poste")
    job_desc = st.text_area("Description complète de l'offre")
    
    if st.button("🚀 Diffuser partout"):
        if title and job_desc:
            st.session_state.job_desc = job_desc # Sauvegarde pour le tri
            st.success("Offre diffusée sur les réseaux de la région : " + region)
            st.balloons()

with t2:
    st.subheader("Identifiants")
    st.text_input("LinkedIn API", type="password")
    st.text_input("Supabase Secret", type="password")
    st.button("Sauvegarder")

with t3:
    st.subheader("Analyse de CV")
    uploaded_cv = st.text_area("Collez le texte du CV ici (ou importez)")
    
    if st.button("🔍 Analyser le matching"):
        if 'job_desc' not in st.session_state:
            st.warning("Veuillez d'abord créer une offre dans l'onglet Diffusion.")
        else:
            # APPEL AU PROCESSOR (Lien JS + Python)
            with st.spinner("Analyse en cours..."):
                result = process_matching(uploaded_cv, st.session_state.job_desc, user_ip)
                
                if isinstance(result, dict):
                    st.markdown(f"""
                    <div class="score-box">
                        <h3>Score : {result.get('score', 0)}%</h3>
                        <p><b>Verdict :</b> {result.get('verdict', '')}</p>
                        <p>✅ <b>Points forts :</b> {', '.join(result.get('points_forts', []))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(result)

with t4:
    st.write("Statistiques de diffusion en temps réel.")
    st.table(pd.DataFrame({"Canal": ["LinkedIn", "Indeed"], "Vues": [124, 89]}))

# --- 7. FOOTER ---
st.markdown(f"""
    <div class="footer">
        <small>© 2026 <b>ZAXX.app</b> | OmniPost est une marque de RAKOTOBE Liliane. 
        <a href="mailto:creationsites06@gmail.com" style="color:#00467F; margin-left:10px;">📩 Support</a></small>
    </div>
    """, unsafe_allow_html=True)
