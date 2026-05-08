import streamlit as st
import pandas as pd
from PIL import Image
from streamlit_javascript import st_javascript

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="OmniPost Global", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
    :root { --primary: #00467F; --cyan: #4FA9D1; --green: #22c55e; }
    .stButton>button { background-color: var(--primary); color: white; border-radius: 8px; width: 100%; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f0f2f6; border-radius: 5px; padding: 10px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background: white; text-align: center; padding: 8px; border-top: 1px solid #ddd; z-index: 100; }
    .license-alert { background-color: #fff5f5; border: 2px solid #ff4b4b; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTION DES LANGUES (20+ LANGUES) ---
# Dictionnaire simplifié pour la démo (extensible à 20 langues)
LANG_DATA = {
    "Français 🇫🇷": {"code": "FR", "region": "France"},
    "English (US) 🇺🇸": {"code": "US", "region": "Global/USA"},
    "English (UK) 🇬🇧": {"code": "UK", "region": "Global/UK"},
    "Malagasy 🇲🇬": {"code": "MG", "region": "Madagascar"},
    "Deutsch 🇩🇪": {"code": "DE", "region": "Germany"},
    "Español 🇪🇸": {"code": "ES", "region": "Spain"},
    "中文 🇨🇳": {"code": "CN", "region": "China"},
    "日本語 🇯🇵": {"code": "JP", "region": "Japan"},
    "Português 🇧🇷": {"code": "BR", "region": "Brazil"}
}

if 'lang' not in st.session_state:
    st.session_state.lang = "Français 🇫🇷"

# --- 3. BASE DE DONNÉES DIFFUSEURS ---
DIFFUSEURS = {
    "France": ["France Travail", "Indeed", "APEC", "Welcome to the Jungle", "Remote.com", "LinkedIn", "Facebook Pro", "Instagram"],
    "Global/USA": ["Indeed (Global)", "LinkedIn", "Monster", "Glassdoor", "Remote.com", "Twitter/X"],
    "Global/UK": ["Reed.co.uk", "LinkedIn", "Indeed UK", "Totaljobs"],
    "Madagascar": ["Portal Job MG", "LinkedIn", "Facebook Pages", "Remote.com"]
}

# --- 4. RÉCUPÉRATION IP & COMPTEUR ---
user_ip = st_javascript("await fetch('https://api.ipify.org?format=json').then(res => res.json()).then(data => data.ip)")

if 'credentials' not in st.session_state:
    st.session_state.credentials = {}  # Stockage fictif des IDs
if 'ads_count' not in st.session_state:
    st.session_state.ads_count = 0

is_limit_reached = st.session_state.ads_count >= 1

# --- 5. SIDEBAR : LOGO & LANGUES ---
with st.sidebar:
    try:
        logo = Image.open('logo_omnipost.jpg')
        st.image(logo, use_container_width=True)
    except:
        st.title("OMNIPOST")
    
    st.divider()
    st.subheader("🌐 Langue / Language")
    st.session_state.lang = st.selectbox("Choisir la langue", list(LANG_DATA.keys()))
    
    current_region = LANG_DATA[st.session_state.lang]["region"]
    st.info(f"Région active : {current_region}")

    if is_limit_reached:
        st.error("🔒 Essai terminé")
    else:
        st.success("✅ 1 Annonce Multi-diffusion offerte")

# --- 6. DASHBOARD ---
st.title("🌍 OmniPost Multi-Posting Global")

tabs = st.tabs(["📢 Diffuser l'offre", "🔑 Mes Comptes", "📊 Rapports"])

# --- ONGLET : DIFFUSION ---
with tabs[0]:
    if is_limit_reached:
        st.markdown("""
            <div class="license-alert">
                <h3>Limite d'essai atteinte</h3>
                <p>Pour continuer à diffuser sur tous vos réseaux et agences intérim, activez votre licence.</p>
                <a href="#" style="background:#22c55e; color:white; padding:10px; text-decoration:none; border-radius:5px;">Activer la Licence Pro</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("Configuration de l'annonce")
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Intitulé du poste")
            desc = st.text_area("Description du poste")
        
        with col2:
            st.write("🎯 **Cibles de diffusion**")
            # Choix dynamique selon la région
            options = DIFFUSEURS.get(current_region, DIFFUSEURS["Global/USA"])
            targets = st.multiselect("Choisir les plateformes", options)
            
            interim = st.toggle("Envoyer aux agences d'intérim locales")
            if interim:
                dept = st.text_input("Département ou Ville", placeholder="ex: 06 ou Paris")
                st.caption("L'IA va lister les agences (Adecco, Manpower, Randstad...) de cette zone.")

        if st.button("🚀 Diffuser partout d'un seul clic"):
            if title and targets:
                st.session_state.ads_count += 1
                st.success(f"Annonce envoyée vers : {', '.join(targets)}")
                if interim:
                    st.info(f"📧 Email envoyé aux agences d'intérim de {dept}")
                st.rerun()
            else:
                st.warning("Veuillez remplir le titre et choisir au moins un diffuseur.")

# --- ONGLET : MES COMPTES (IDENTIFIANTS) ---
with tabs[1]:
    st.subheader("🔑 Gestion des identifiants enregistrés")
    st.write("Enregistrez vos comptes pour ne plus avoir à vous connecter.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Réseaux Sociaux**")
        st.text_input("Facebook Page ID", value=st.session_state.credentials.get('fb', ''))
        st.text_input("LinkedIn Business ID")
    with col_b:
        st.write("**Job Boards**")
        st.text_input("Indeed Account")
        st.text_input("Welcome to the Jungle ID")
    
    if st.button("💾 Sauvegarder mes identifiants"):
        st.toast("Identifiants sécurisés et sauvegardés !")

# --- ONGLET : RAPPORTS (GRATUITÉ) ---
with tabs[2]:
    st.subheader("📈 Suivi des crédits diffuseurs")
    st.write("OmniPost vous rappelle vos quotas gratuits sur les plateformes tierces.")
    
    data = {
        "Diffuseur": ["Indeed", "France Travail", "LinkedIn", "Welcome to the Jungle"],
        "Offre": ["1 gratuite/mois", "Illimité (Public)", "3 gratuites", "Payant (Licence requise)"],
        "Statut": ["Disponible", "Disponible", "Dernier essai", "Abonnement requis"]
    }
    st.table(pd.DataFrame(data))

# --- 7. FOOTER ---
st.markdown(f"""
    <div class="footer">
        Créée par <b>RAKOTOBE Liliane</b> | 
        <a href="mailto:creationsites06@gmail.com" title="Contact">📩</a>
    </div>
    """, unsafe_allow_html=True)
