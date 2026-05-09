import streamlit as st
import pandas as pd
import streamlit_webrtc as webrtc
from PIL import Image
from streamlit_javascript import st_javascript

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
    
    /* Footer fixe */
    .footer { 
        position: fixed; left: 0; bottom: 0; width: 100%; 
        background: white; text-align: center; padding: 15px; 
        border-top: 1px solid #ddd; z-index: 100; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTILINGUE (20 LANGUES) ---
LANG_DATA = {
    "Français 🇫🇷": {"region": "France"},
    "English (US) 🇺🇸": {"region": "Global/USA"},
    "English (UK) 🇬🇧": {"region": "Global/UK"},
    "Malagasy 🇲🇬": {"region": "Madagascar"},
    "Deutsch 🇩🇪": {"region": "Germany"},
    "Español 🇪🇸": {"region": "Spain"},
    "Italiano 🇮🇹": {"region": "Global"},
    "Português 🇧🇷": {"region": "Brazil"},
    "Русский 🇷🇺": {"region": "Global"},
    "日本語 🇯🇵": {"region": "Japan"},
    "한국어 🇰🇷": {"region": "Global"},
    "हिन्दी 🇮🇳": {"region": "Global"},
    "العربية 🇸🇦": {"region": "Global"},
    "Türkçe 🇹🇷": {"region": "Global"},
    "Polski 🇵🇱": {"region": "Global"},
    "Tiếng Việt 🇻🇳": {"region": "Global"},
    "ไทย 🇹🇭": {"region": "Global"},
    "Nederlands 🇳🇱": {"region": "Global"},
    "Bahasa Indonesia 🇮🇩": {"region": "Global"},
    "Svenska 🇸🇪": {"region": "Global"}
}

# --- 3. RÉSEAUX DE DIFFUSION ---
DIFFUSEURS = {
    "France": ["France Travail", "Indeed", "APEC", "Welcome to the Jungle", "LinkedIn", "Hellowork"],
    "Global/USA": ["Indeed (US)", "LinkedIn", "Monster", "Glassdoor", "ZipRecruiter"],
    "Madagascar": ["Portal Job MG", "Orange Jobs", "LinkedIn", "Facebook Jobs"],
    "Global": ["LinkedIn", "Indeed (Global)", "Remote.com", "Facebook Pro", "Instagram"]
}

# --- 4. SÉCURITÉ IP & LIMITES ---
user_ip = st_javascript("await fetch('https://api.ipify.org?format=json').then(res => res.json()).then(data => data.ip)")

if 'ads_count' not in st.session_state: st.session_state.ads_count = 0
if 'used_ips' not in st.session_state: st.session_state.used_ips = []
if 'credentials' not in st.session_state: st.session_state.credentials = {}

is_blocked = user_ip in st.session_state.used_ips
limit_reached = st.session_state.ads_count >= 1 or is_blocked

# --- 5. SIDEBAR ---
with st.sidebar:
    try:
        logo = Image.open('logo_omnipost.jpg')
        st.image(logo, use_container_width=True)
    except:
        st.title("ZAXX.app")
    
    st.divider()
    selected_lang = st.selectbox("🌐 Langue du Dashboard", list(LANG_DATA.keys()))
    region = LANG_DATA[selected_lang]["region"]
    
    st.info(f"Région de diffusion : {region}")
    
    if limit_reached:
        st.error("🔒 Licence d'essai expirée")
    else:
        st.success("✅ 1 Crédit de diffusion offert")

# --- 6. DASHBOARD ZAXX / OMNIPOST ---
st.title("Zaxx : Multipostage Intelligent")

t1, t2, t3, t4 = st.tabs(["📢 Diffuser l'offre", "🔑 Mes Comptes", "📂 Tri IA & Vidéo", "📈 Analytique"])

# --- TAB 1 : DIFFUSION ---
with t1:
    if limit_reached:
        st.markdown(f"""
            <div class="license-alert">
                <h2>Identifiant de session : {user_ip}</h2>
                <p>Votre offre de bienvenue OmniPost sur <b>zaxx.app</b> a été utilisée.</p>
                <p>Pour débloquer la diffusion illimitée vers toutes les agences d'intérim et réseaux sociaux :</p>
                <br>
                <a href="#" class="buy-button">💳 Activer ma Licence Pro sur Zaxx.app</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("Nouvelle publication multicanale")
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Titre du poste à pourvoir")
            targets = st.multiselect("Canaux Jobboards", DIFFUSEURS.get(region, DIFFUSEURS["Global"]))
        with c2:
            social = st.multiselect("Canaux Sociaux", ["LinkedIn Business", "Facebook Page", "Instagram Ads", "X / Twitter"])
            interim = st.toggle("Alerter les agences d'intérim locales")
            
        if st.button("🚀 Diffuser sur tous les canaux"):
            if title and (targets or social):
                st.session_state.used_ips.append(user_ip)
                st.session_state.ads_count += 1
                st.balloons()
                st.success("Diffusion en cours sur zaxx.app...")
                st.rerun()

# --- TAB 2 : COMPTES ---
with t2:
    st.subheader("🔑 Gestionnaire de clés & identifiants")
    st.caption("Enregistrez vos accès une seule fois pour automatiser vos prochaines publications.")
    col_a, col_b = st.columns(2)
    with col_a:
        st.text_input("LinkedIn API Key", type="password")
        st.text_input("Facebook Page Token", type="password")
    with col_b:
        st.text_input("Identifiant Indeed Employer")
        st.text_input("Emails Agences Intérim (séparés par des virgules)")
    
    if st.button("💾 Mémoriser sur Zaxx"):
        st.toast("Identifiants sauvegardés avec succès !")

# --- TAB 3 : TRI IA ---
with t3:
    st.subheader("📂 Analyse des candidatures entrantes")
    if st.session_state.ads_count > 0:
        st.write("Candidat matché : **Alice Durand** (94% de correspondance)")
        if st.button("Lancer l'entretien Vidéo"):
            webrtc.webrtc_streamer(key="video")
    else:
        st.info("Les CV apparaîtront ici après votre première diffusion.")

# --- TAB 4 : RAPPORTS ---
with t4:
    st.subheader("📊 État des services tiers")
    df = pd.DataFrame({
        "Service": ["LinkedIn", "Indeed", "Agences Intérim", "Facebook"],
        "Statut": ["Connecté", "Prêt", "En attente", "Connecté"],
        "Crédits": ["3 restants", "1 gratuit", "Illimité", "Illimité"]
    })
    st.table(df)

# --- 7. FOOTER (Mention Propriété Zaxx / OmniPost) ---
st.markdown(f"""
    <div class="footer">
        <small>
            © 2026 <b>ZAXX.app</b> | OmniPost est une marque de RAKOTOBE Liliane. 
            Sous Licence Commerciale Exclusive.
            <a href="mailto:creationsites06@gmail.com?subject=Support%20OmniPost%20Zaxx" 
               title="Contacter le support technique" 
               style="color:#00ced1; text-decoration:none; margin-left:15px; font-size:1.1rem;">
               📩 Support Technique
            </a>
        </small>
    </div>
    """, unsafe_allow_html=True)
