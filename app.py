import streamlit as st
from supabase import create_client, Client

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- LANGUES ---
LANGUAGES = {
    "Français": {
        "welcome": "Bienvenue sur zipngo",
        "desc": "L'application qui révolutionne le recrutement.",
        "dash": "Tableau de bord", "profile": "Relooking & ATS", 
        "prop": "Propulsion de candidature", "match": "Matchs & Entretiens", 
        "off": "Diffusion d'offres", "acc": "Mon Compte"
    }
}
t = LANGUAGES["Français"]

# --- SÉLECTEUR LANGUE (Haut) ---
col_lang, _ = st.columns([1, 10])
with col_lang:
    if "lang" not in st.session_state: st.session_state.lang = "Français"
    st.session_state.lang = st.selectbox("🌐", list(LANGUAGES.keys()))

st.markdown("<h1 style='color: #007BFF;'>zipngo 👍</h1>", unsafe_allow_html=True)

# --- AUTH & SESSION ---
if "auth" not in st.session_state: st.session_state.update({"auth": False, "premium": False, "user_type": "Candidat"})

if not st.session_state.auth:
    st.markdown(f"""
    <div style='background:#f8f9fa; padding:20px; border-radius:10px; border:1px solid #dee2e6;'>
    <h3>{t['welcome']}</h3>
    <p><b>{t['desc']}</b><br>
    Votre identité reste confidentielle jusqu'à ce que vous décidiez de vous dévoiler.</p>
    </div>
    """, unsafe_allow_html=True)
    
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    email = st.text_input("E-mail (Accès magique) :")
    if st.button("✨ Entrer dans l'application"):
        st.session_state.update({"auth": True, "user_email": email, "user_type": role})
        st.rerun()

else:
    with st.sidebar:
        if st.session_state.get("premium"): st.success("✨ Premium")
        menu = st.radio("Navigation", [t["dash"], t["profile"], t["prop"], t["match"], t["off"], t["acc"]])
        if st.button("🚪 Déconnexion"): st.session_state.auth = False; st.rerun()

    # --- TABLEAU DE BORD AVEC MODE D'EMPLOI ---
    if menu == t["dash"]:
        st.header(t["dash"])
        if st.session_state.user_type == "Candidat":
            st.markdown("""### 📖 Guide du Candidat
            1. **Relooking & ATS :** Déposez votre CV, l'IA l'optimise pour passer les filtres.
            2. **Propulsion :** Diffusez votre profil anonyme vers les opportunités ciblées.
            3. **Entretien :** Proposez un créneau et rencontrez votre recruteur en visio.""")
        else:
            st.markdown("""### 📖 Guide de l'Employeur
            1. **Diffusion :** Publiez votre offre ; elle est diffusée anonymement.
            2. **Matchs :** Validez un candidat, le voile de l'anonymat est alors levé.
            3. **Entretien :** Planifiez votre rencontre via l'outil intégré.""")
    
    # --- RELOOKING & ATS ---
    elif menu == t["profile"]:
        st.header(t["profile"])
        st.file_uploader("Déposer mon CV")
        if st.button("✨ Optimiser mon profil avec l'IA"): 
            st.write("✅ Votre CV a été enrichi. Score ATS : Passé de 45% à 88%.")

    # --- PROPULSION ---
    elif menu == t["prop"]:
        st.header(t["prop"])
        if st.button("🚀 Propulser ma candidature"):
            st.success("Candidature transmise aux opportunités ciblées.")
            st.caption("Votre identité est protégée jusqu'à l'acceptation.")

    # --- MATCHS & ENTRETIEN ---
    elif menu == t["match"]:
        st.header(t["match"])
        st.write("📅 **Planification :**")
        col1, col2 = st.columns(2)
        with col1: date = st.date_input("Choisir une date")
        with col2: heure = st.time_input("Choisir une heure")
        if st.button("Confirmer la proposition"): st.write("Proposition envoyée.")
        st.link_button("Rejoindre l'entretien vidéo", "https://meet.jit.si/zipngo")

    # --- DIFFUSION OFFRES ---
    elif menu == t["off"]:
        st.header(t["off"])
        if st.button("📢 Diffuser mon offre"): 
            st.balloons()
            st.success("Offre diffusée sur vos réseaux professionnels.")

    # --- MON COMPTE (ADMIN) ---
    elif menu == t["acc"]:
        st.header(t["acc"])
        st.write("Paramètres : Anonymat actif.")
        if st.session_state.user_email == "creationsites06@gmail.com":
            st.download_button("📥 Export CSV Global", "data", "zipngo_export.csv")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
