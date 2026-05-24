import streamlit as st
from datetime import date

st.set_page_config(page_title="zipngo", layout="wide")

# --- CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .title-zip { color: #000080; font-weight: bold; font-size: 3rem; }
    .title-ngo { color: #1E90FF; font-weight: bold; font-size: 3rem; }
    .subtitle-zaxx { color: #808080; font-size: 0.9rem; font-family: monospace; margin-bottom: 20px; }
    .presentation-box { background-color: #f8f9fa; padding: 25px; border-radius: 10px; border-left: 5px solid #1E90FF; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "user_type": None, "anonymat_leve": False})

# --- PAGE AUTHENTIFICATION ---
if not st.session_state.auth:
    st.markdown('<span class="title-zip">zip</span><span class="title-ngo">ngo</span> 👍', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-zaxx">.zaxx.app</div>', unsafe_allow_html=True)
    
    # Texte de présentation
    st.markdown("""
    <div class="presentation-box">
        <h4>Bienvenue sur zipngo</h4>
        <p>zipngo est la plateforme de recrutement nouvelle génération. Nous simplifions la mise en relation entre talents et recruteurs grâce à une IA de précision. Votre confidentialité est notre priorité : restez anonyme jusqu'au moment de l'entretien et gardez le contrôle total sur vos données professionnelles.</p>
    </div>
    """, unsafe_allow_html=True)
    
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"): st.session_state.update({"auth": True, "user_type": role}); st.rerun()

else:
    # --- NAVIGATION CONNECTÉE ---
    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user_type}**")
        menu = st.radio("Navigation", ["Recherche Talents", "Gestion Entretiens"])
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    # --- LOGIQUE RECRUTEUR ---
    if menu == "Recherche Talents" and st.session_state.user_type == "Employeur":
        st.header("Talents disponibles")
        if st.button("Sélectionner ce profil 👍"):
            st.session_state.profil_selectionne = True
            st.success("Profil sélectionné.")

    # --- LOGIQUE ENTRETIEN ---
    elif menu == "Gestion Entretiens":
        st.header("🤝 Espace Entretiens")
        if not st.session_state.anonymat_leve:
            if st.button("🤝 Lever l'anonymat (Double accord requis) 👍"):
                st.session_state.anonymat_leve = True
                st.rerun()
        else:
            st.success("Anonymat levé.")
            st.link_button("🎥 Salle Visio", "https://meet.jit.si/zipngo-session")

st.markdown(f"--- © {date.today().year} zipngo | .zaxx.app")
