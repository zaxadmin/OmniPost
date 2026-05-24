import streamlit as st
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS (Relief, Couleurs, Masquage menu) ---
st.markdown("""
    <style>
    /* Masquer menu Streamlit pour un rendu App */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%); }
    
    .brand-title { font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 0.1rem; }
    .zip { color: #000080; } /* Bleu Marine */
    .ngo { color: #00FFFF; } /* Cyan */
    .app-url { font-size: 0.9rem; color: #D3D3D3; text-align: center; margin-bottom: 2rem; letter-spacing: 1px; }
    
    .css-1r6slp0, .main .block-container { 
        background-color: white; padding: 40px !important; border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    }
    .stButton>button { 
        background-color: #007BFF !important; color: white !important; border-radius: 12px !important;
        width: 100%; box-shadow: 0 4px 6px rgba(0,123,255,0.2) !important;
    }
    </style>
    
    <div class="brand-title"><span class="zip">zip</span><span class="ngo">ngo</span></div>
    <div class="app-url">zaxx.app</div>
    """, unsafe_allow_html=True)

# --- DICTIONNAIRE ---
LANGUAGES = {"Français": {"label": "Profil & ATS", "welcome": "Bienvenue", "dash": "Tableau de bord", "prop": "Propulsion", "match": "Entretiens", "off": "Diffusion", "acc": "Mon Compte"}}
t = LANGUAGES["Français"]

# --- SESSION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "premium": False, "user_type": "Candidat", "created_at": datetime.date.today()})

if not st.session_state.auth:
    st.markdown("### Bienvenue. L'application qui révolutionne le recrutement.")
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    email = st.text_input("E-mail (Connexion magique) :")
    if st.button("✨ Entrer dans l'application"):
        st.session_state.update({"auth": True, "user_email": email, "user_type": role})
        st.rerun()
else:
    delta = datetime.date.today() - st.session_state.created_at
    is_active = st.session_state.premium or delta.days <= 90

    with st.sidebar:
        if not is_active: st.error("⚠️ Compte en veille (Période d'essai dépassée)")
        elif st.session_state.get("premium"): st.success("✨ Premium Actif")
        else: st.warning("⚠️ Période d'essai")
        menu = st.radio("Navigation", [t["dash"], t["label"], t["prop"], t["match"], t["off"], t["acc"]])
        if st.button("🚪 Déconnexion"): st.session_state.auth = False; st.rerun()

    if menu == t["dash"]:
        st.header(t["dash"])
        st.info("📖 **Guide :** " + ("Optimisez votre CV, propulsez-le anonymement." if st.session_state.user_type == "Candidat" else "Diffusez anonymement, validez les matchs."))
    
    elif menu == t["label"]:
        st.file_uploader("Déposer mon CV")
        if st.checkbox("🌍 Je cherche des postes en Remote"): st.success("Filtre géographique levé.")
        if st.button("✨ Optimiser avec l'IA"): st.write("✅ Score ATS : 88%.")

    elif menu == t["prop"]:
        if st.button("🚀 Propulser ma candidature"): st.success("Transmis. Identité protégée.")

    elif menu == t["match"]:
        col1, col2 = st.columns(2)
        with col1: st.date_input("Date")
        with col2: st.time_input("Heure")
        if st.button("✅ Confirmer proposition"): st.write("Proposition envoyée.")
        st.link_button("🎥 Rejoindre la salle", "https://meet.jit.si/zipngo", type="primary")

    elif menu == t["off"]:
        if st.checkbox("🌍 Offre Remote (Lève restrictions)"): st.success("Portée mondiale activée.")
        if st.button("📢 Diffuser mon offre"): st.balloons()

    elif menu == t["acc"]:
        st.header(t["acc"])
        with st.expander("⚖️ Mentions Légales"): st.write("Plateforme de mise en relation. Aucune responsabilité sur la véracité des données.")
        with st.expander("📜 CGV"): st.write("Mise en veille après 90 jours sans Premium. Suppression sur demande.")
        st.link_button("📧 Support & Suppression", "mailto:creationsites06@gmail.com")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
