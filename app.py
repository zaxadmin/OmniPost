import streamlit as st
import pandas as pd
import streamlit_webrtc as webrtc
from PIL import Image
from streamlit_javascript import st_javascript

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="OmniPost.app", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    :root { --primary-blue: #00467F; --secondary-cyan: #4FA9D1; }
    h1, h2, h3 { color: var(--primary-blue) !important; }
    .stButton>button { background-color: var(--primary-blue); color: white; border-radius: 8px; border: none; }
    .stButton>button:hover { background-color: var(--secondary-cyan); }
    .buy-button { display: inline-block; padding: 15px 30px; background-color: #22c55e; color: white !important; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 18px; margin-top: 10px; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: white; text-align: center; padding: 10px; border-top: 1px solid #e2e8f0; z-index: 100; font-size: 14px; }
    .footer a { color: var(--primary-blue); text-decoration: none; font-size: 20px; margin-left: 5px; }
    .license-alert { background-color: #fef2f2; border: 2px solid #ef4444; padding: 30px; border-radius: 15px; text-align: center; color: #b91c1c; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DÉTECTEUR D'IP & SÉCURITÉ ---
# On récupère l'IP via un petit script JS
user_ip = st_javascript("await fetch('https://api.ipify.org?format=json').then(res => res.json()).then(data => data.ip)")

if 'used_ips' not in st.session_state:
    # Dans une vraie app, cela viendrait d'une base de données externe
    st.session_state.used_ips = []

if 'ads_count' not in st.session_state:
    st.session_state.ads_count = 0

# Vérification : l'IP a-t-elle déjà publié ?
is_ip_blocked = user_ip in st.session_state.used_ips
is_limit_reached = st.session_state.ads_count >= 1 or is_ip_blocked

# --- 3. DONNÉES DE DÉMO ---
if 'candidates' not in st.session_state:
    st.session_state.candidates = [
        {"Nom": "Marc Riva", "Score": 96, "Statut": "En attente", "Handicap": True},
        {"Nom": "Alice Vion", "Score": 84, "Statut": "En attente", "Handicap": False}
    ]

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    try:
        logo = Image.open('logo_omnipost.jpg')
        st.image(logo, use_container_width=True)
    except:
        st.title("🚀 OMNIPOST")
    
    st.divider()
    st.write(f"🌐 Votre IP : `{user_ip if user_ip else 'Détection...'}`")
    
    if is_limit_reached:
        st.error("🔒 Limitation active (IP/Email)")
    else:
        st.success("✅ 1 essai gratuit disponible")

# --- 5. DASHBOARD PRINCIPAL ---
st.title("OmniPost : Recrutement Prédictif")

tabs = st.tabs(["📢 Publication", "📂 Tri des CV (IA)", "📹 Salon Vidéo"])

# --- ONGLET 1 : PUBLICATION ---
with tabs[0]:
    if is_limit_reached:
        st.markdown(f"""
            <div class="license-alert">
                <h2>🔒 Accès Limité détecté</h2>
                <p>Notre système indique qu'une annonce a déjà été publiée depuis cet appareil ou ce réseau.</p>
                <p>Pour continuer à utiliser OmniPost sans restriction :</p>
                <br>
                <a href="#" class="buy-button">💳 Débloquer la Licence Pro</a>
                <p style="margin-top:15px; font-size:11px;">Identifiant de session : {user_ip}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("Publiez votre offre d'essai")
        job_name = st.text_input("Titre du poste")
        st.toggle("Option inclusion handicap", value=True)
            
        if st.button("🚀 Publier maintenant"):
            if job_name:
                # On enregistre l'IP pour bloquer les futurs essais
                st.session_state.used_ips.append(user_ip)
                st.session_state.ads_count += 1
                st.session_state.current_job = job_name
                st.success("Annonce publiée ! L'IA commence le tri.")
                st.rerun()
            else:
                st.warning("Veuillez saisir un titre.")

# --- ONGLET 2 : GESTION DES CV ---
with tabs[1]:
    if st.session_state.ads_count == 0 and not is_ip_blocked:
        st.info("Publiez une annonce pour activer le tri.")
    else:
        st.subheader("Candidats triés par l'IA")
        for i, row in pd.DataFrame(st.session_state.candidates).iterrows():
            with st.expander(f"{row['Nom']} - Matching {row['Score']}%"):
                if st.button("Valider", key=f"v_{i}"):
                    st.session_state.candidates[i]['Statut'] = "🤝 Validé"
                    st.rerun()

# --- ONGLET 3 : SALON VIDÉO ---
with tabs[2]:
    confirmes = [c['Nom'] for c in st.session_state.candidates if c['Statut'] == "🤝 Validé"]
    if confirmes:
        st.selectbox("Démarrer l'appel avec :", confirmes)
        webrtc.webrtc_streamer(key="video")
    else:
        st.warning("Aucun candidat validé.")

# --- 6. FOOTER ---
st.markdown(f"""
    <div class="footer">
        Créée par <b>RAKOTOBE Liliane</b> 
        <a href="mailto:creationsites06@gmail.com" title="Contacter Liliane">📩</a>
    </div>
    """, unsafe_allow_html=True)
