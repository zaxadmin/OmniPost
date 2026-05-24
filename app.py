import streamlit as st
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%); }
    
    .brand-title { font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 0.1rem; }
    .zip { color: #000080; } /* Bleu Marine */
    .ngo { color: #00FFFF; } /* Cyan */
    .app-url { font-size: 0.95rem; color: #6c757d; text-align: center; margin-bottom: 2rem; letter-spacing: 1.5px; font-weight: 500; }
    
    .css-1r6slp0, .main .block-container { 
        background-color: white; padding: 40px !important; border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    }
    .stButton>button { 
        background-color: #007BFF !important; color: white !important; border-radius: 12px !important;
        width: 100%; border: none !important; box-shadow: 0 4px 6px rgba(0,123,255,0.2) !important;
    }
    </style>
    <div class="brand-title"><span class="zip">zip</span><span class="ngo">ngo</span></div>
    <div class="app-url">.zaxx.app</div>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "premium": False, "profile_completed": False, "created_at": datetime.date.today(), "user_type": "Candidat"})

# --- LOGIQUE DE CONNEXION ---
if not st.session_state.auth:
    st.markdown("### Bienvenue. L'application qui révolutionne le recrutement.")
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer dans l'application"):
        st.session_state.update({"auth": True, "user_type": role})
        st.rerun()

# --- ONBOARDING OBLIGATOIRE ---
elif not st.session_state.profile_completed:
    st.header("✨ Finalisez votre inscription")
    with st.form("onboarding"):
        nom = st.text_input("Nom & Prénom")
        tel = st.text_input("Téléphone")
        email_pro = st.text_input("Email de contact")
        if st.session_state.user_type == "Employeur":
            entreprise = st.text_input("Nom de l'entreprise")
            site = st.text_input("Site Web (Facultatif)")
        else:
            secteur = st.selectbox("Secteur d'activité", ["Tech", "Finance", "Santé", "Autre"])
        if st.form_submit_button("Valider mes informations"):
            st.session_state.profile_completed = True
            st.rerun()
    st.stop()

# --- APPLICATION ---
else:
    t = {"dash": "Tableau de bord", "label": "Profil", "prop": "Propulsion", "match": "Entretiens", "off": "Diffusion", "acc": "Mon Compte"}
    with st.sidebar:
        if st.session_state.premium: st.success("✨ Premium Actif")
        else: st.warning("⚠️ Essai gratuit")
        menu = st.radio("Navigation", list(t.values()))
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    if menu == t["dash"]:
        st.header(t["dash"])
        st.info("Guide : " + ("Optimisez votre CV, propulsez-le anonymement." if st.session_state.user_type == "Candidat" else "Diffusez anonymement, validez les matchs."))
    elif menu == t["label"]:
        st.file_uploader("Déposer mon CV")
        if st.session_state.user_type == "Candidat":
            secteur = st.selectbox("Modifier mon secteur", ["Tech", "Finance", "Santé", "Autre"])
    elif menu == t["match"]:
        st.link_button("🎥 Rejoindre la salle", "https://meet.jit.si/zipngo", type="primary")
    elif menu == t["acc"]:
        st.header(t["acc"])
        with st.expander("⚖️ Mentions Légales"): st.write("Responsabilité limitée.")
        with st.expander("📜 CGV"): st.write("Mise en veille après 90j sans Premium.")
        st.link_button("📧 Support & Suppression", "mailto:creationsites06@gmail.com")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
