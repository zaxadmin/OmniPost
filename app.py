import streamlit as st
import pandas as pd
import streamlit_webrtc as webrtc
from PIL import Image
from streamlit_javascript import st_javascript

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="OmniPost.app", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    :root { --primary: #00467F; --cyan: #4FA9D1; --green: #22c55e; }
    .stButton>button { background-color: var(--primary); color: white; border-radius: 8px; width: 100%; }
    .buy-button { 
        display: inline-block; padding: 15px 30px; background-color: var(--green); 
        color: white !important; border-radius: 10px; text-decoration: none; 
        font-weight: bold; font-size: 18px; margin: 10px 0; text-align: center;
    }
    .license-alert { background-color: #fff5f5; border: 2px solid #ff4b4b; padding: 20px; border-radius: 10px; text-align: center; }
    
    /* Style du Footer fixe */
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background: white; text-align: center; padding: 15px; 
        border-top: 1px solid #ddd; z-index: 100; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SYSTÈME DE LANGUES & RÉGIONS ---
LANG_DATA = {
    "Français 🇫🇷": {"code": "FR", "region": "France"},
    "English (US) 🇺🇸": {"code": "US", "region": "Global/USA"},
    "English (UK) 🇬🇧": {"code": "UK", "region": "Global/UK"},
    "Malagasy 🇲🇬": {"code": "MG", "region": "Madagascar"},
    "Deutsch 🇩🇪": {"code": "DE", "region": "Germany"},
    "Español 🇪🇸": {"code": "ES", "region": "Spain"},
    "Italiano 🇮🇹": {"code": "IT", "region": "Global"},
    "Português 🇧🇷": {"code": "BR", "region": "Brazil"},
    "Русский 🇷🇺": {"code": "RU", "region": "Global"},
    "日本語 🇯🇵": {"code": "JP", "region": "Japan"},
    "한국어 🇰🇷": {"code": "KR", "region": "Global"},
    "हिन्दी 🇮🇳": {"code": "IN", "region": "Global"},
    "العربية 🇸🇦": {"code": "SA", "region": "Global"},
    "Türkçe 🇹🇷": {"code": "TR", "region": "Global"},
    "Polski 🇵🇱": {"code": "PL", "region": "Global"},
    "Tiếng Việt 🇻🇳": {"code": "VN", "region": "Global"},
    "ไทย 🇹🇭": {"code": "TH", "region": "Global"},
    "Nederlands 🇳🇱": {"code": "NL", "region": "Global"},
    "Bahasa Indonesia 🇮🇩": {"code": "ID", "region": "Global"},
    "Svenska 🇸🇪": {"code": "SE", "region": "Global"}
}

# --- 3. BASE DE DONNÉES DIFFUSEURS PAR RÉGION ---
DIFFUSEURS = {
    "France": ["France Travail", "Indeed", "APEC", "Welcome to the Jungle", "LinkedIn", "Meteojob", "HelloWork"],
    "Global/USA": ["Indeed (US)", "LinkedIn", "Monster", "Glassdoor", "ZipRecruiter", "Dice"],
    "Global/UK": ["Reed.co.uk", "LinkedIn", "Indeed UK", "Totaljobs", "Guardian Jobs"],
    "Madagascar": ["Portal Job MG", "LinkedIn", "Orange Jobs MG", "Facebook Community"],
    "Global": ["LinkedIn", "Indeed (Global)", "Remote.com", "Facebook Pro", "Twitter/X", "Instagram"]
}

# --- 4. LOGIQUE DE SÉCURITÉ & SESSION ---
user_ip = st_javascript("await fetch('https://api.ipify.org?format=json').then(res => res.json()).then(data => data.ip)")

if 'used_ips' not in st.session_state: st.session_state.used_ips = []
if 'ads_count' not in st.session_state: st.session_state.ads_count = 0
if 'credentials' not in st.session_state: st.session_state.credentials = {}

is_ip_blocked = user_ip in st.session_state.used_ips
is_limit_reached = st.session_state.ads_count >= 1 or is_ip_blocked

# --- 5. SIDEBAR (LOGO & LANGUE) ---
with st.sidebar:
    try:
        logo = Image.open('logo_omnipost.jpg')
        st.image(logo, use_container_width=True)
    except:
        st.title("OMNIPOST.app")
    
    st.divider()
    selected_lang_name = st.selectbox("🌐 Sélectionner Langue", list(LANG_DATA.keys()))
    st.session_state.lang = LANG_DATA[selected_lang_name]["code"]
    region = LANG_DATA[selected_lang_name]["region"]
    
    st.write(f"📍 Zone : **{region}**")
    if is_limit_reached:
        st.error("🔒 Limite d'essai atteinte")
    else:
        st.success("✅ 1 diffusion gratuite disponible")

# --- 6. DASHBOARD PRINCIPAL ---
st.title("🚀 OmniPost : Multi-diffusion IA")

tabs = st.tabs(["📢 Diffuser", "🔑 Mes Identifiants", "📂 Suivi CV & Vidéo", "📊 Rapports"])

# --- ONGLET 1 : DIFFUSION ---
with tabs[0]:
    if is_limit_reached:
        st.markdown(f"""
            <div class="license-alert">
                <h2>Accès Limité (IP: {user_ip})</h2>
                <p>Votre essai gratuit est terminé. Pour diffuser sur tous les jobboards mondiaux et réseaux sociaux :</p>
                <a href="#" class="buy-button">💳 Débloquer OmniPost.app Illimité</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader(f"Paramétrage de l'offre ({region})")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Titre du poste")
            platforms = st.multiselect("Diffuseurs ciblés", DIFFUSEURS.get(region, DIFFUSEURS["Global"]))
        with col2:
            social = st.multiselect("Réseaux Sociaux", ["Facebook Pro", "Facebook Perso", "LinkedIn Page", "Instagram", "Twitter/X"])
            interim = st.toggle("Envoyer aux agences d'intérim locales")
            if interim:
                dept = st.text_input("Département / Ville pour Intérim")

        if st.button("🚀 Lancer la multi-diffusion"):
            if title and (platforms or social):
                st.session_state.used_ips.append(user_ip)
                st.session_state.ads_count += 1
                st.success("Annonce en cours de déploiement...")
                st.rerun()

# --- ONGLET 2 : IDENTIFIANTS ---
with tabs[1]:
    st.subheader("🔐 Vos comptes enregistrés")
    st.caption("Vos identifiants sont sauvegardés localement pour vos prochaines diffusions.")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.credentials['fb'] = st.text_input("Facebook ID", value=st.session_state.credentials.get('fb', ''))
        st.session_state.credentials['li'] = st.text_input("LinkedIn API Key")
    with c2:
        st.session_state.credentials['in'] = st.text_input("Indeed Employer Login")
        st.session_state.credentials['it'] = st.text_input("Identifiants Agences Intérim")
    
    if st.button("💾 Sauvegarder les accès"):
        st.toast("Identifiants mémorisés !")

# --- ONGLET 3 : CV & VIDÉO ---
with tabs[2]:
    st.subheader("📂 Gestion des Candidats & Entretiens")
    if st.session_state.ads_count > 0:
        st.write("Candidat test : **Marc Riva** (Score IA: 96%)")
        if st.button("Démarrer l'entretien Vidéo"):
            webrtc.webrtc_streamer(key="video")
    else:
        st.info("Aucune donnée disponible. Diffusez une annonce pour voir les CV.")

# --- ONGLET 4 : RAPPORTS ---
with tabs[3]:
    st.subheader("📊 État des quotas gratuits")
    st.write("Suivi des offres gratuites des diffuseurs tiers :")
    data = {"Plateforme": ["Indeed", "LinkedIn", "Facebook"], "Gratuité": ["1 / mois", "3 restantes", "Illimité"], "Statut": ["OK", "Warning", "OK"]}
    st.table(pd.DataFrame(data))

# --- 7. FOOTER (Licence Commerciale) ---
st.markdown(f"""
    <div class="footer">
        <small>
            © 2026 OMNIPOST.app | Sous Licence Commerciale Exclusive - Propriété de RAKOTOBE Liliane 
            <a href="mailto:creationsites06@gmail.com?subject=Support%20OmniPost" 
               title="Contacter le support" 
               style="color:#00ced1; text-decoration:none; margin-left:12px; font-size:1.2rem;">
               📩
            </a>
        </small>
    </div>
    """, unsafe_allow_html=True)
