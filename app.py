import streamlit as st
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS (Relief, Couleurs, Masquage menu) ---
st.markdown("""
    <style>
    /* Masquer menu Streamlit et éléments superflus */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%); }
    
    /* Design Titre */
    .brand-title { font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 0.1rem; }
    .zip { color: #000080; } /* Bleu Marine */
    .ngo { color: #00FFFF; } /* Cyan */
    .app-url { font-size: 0.95rem; color: #6c757d; text-align: center; margin-bottom: 2rem; letter-spacing: 1.5px; font-weight: 500; }
    
    /* Bloc central avec relief */
    .css-1r6slp0, .main .block-container { 
        background-color: white; padding: 40px !important; border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    }
    
    /* Boutons */
    .stButton>button { 
        background-color: #007BFF !important; color: white !important; border-radius: 12px !important;
        width: 100%; border: none !important; box-shadow: 0 4px 6px rgba(0,123,255,0.2) !important;
    }
    </style>
    <div class="brand-title"><span class="zip">zip</span><span class="ngo">ngo</span> 👍</div>
    <div class="app-url">.zaxx.app</div>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "premium": False, "profile_completed": False, "created_at": datetime.date.today(), "user_type": "Candidat"})

# --- PAGE DE CONNEXION ---
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
    st.stop() # Bloque l'accès tant que le profil n'est pas complet

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
        with st.expander("⚙️ Paramètres"):
            new_email = st.text_input("Changer mon email de connexion")
            if st.button("Mettre à jour"): st.success("Email modifié.")
        with st.expander("⚖️ Mentions Légales"): st.write("Plateforme de mise en relation. Nous ne sommes pas responsables de la véracité des données.")
        with st.expander("📜 CGV"): st.write("Mise en veille après 90j sans Premium. Suppression sur demande.")
        st.link_button("📧 Support & Suppression", "mailto:creationsites06@gmail.com")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
