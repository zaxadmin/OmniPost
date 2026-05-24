import streamlit as st
import pandas as pd
import json
from groq import Groq
from datetime import date

st.set_page_config(page_title="zipngo", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    .title-zip { color: #000080; font-weight: bold; font-size: 3rem; }
    .title-ngo { color: #1E90FF; font-weight: bold; font-size: 3rem; }
    .subtitle-zaxx { color: #808080; font-size: 0.9rem; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "user_type": None, "anonymat_leve": False})

# --- PAGE AUTH ---
if not st.session_state.auth:
    st.markdown('<span class="title-zip">zip</span><span class="title-ngo">ngo</span> 👍', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-zaxx">.zaxx.app</div>', unsafe_allow_html=True)
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"): st.session_state.update({"auth": True, "user_type": role}); st.rerun()

else:
    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user_type}**")
        menu = st.radio("Navigation", ["Recherche Talents", "Gestion Entretiens"])
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    # --- LOGIQUE RECRUTEUR : SÉLECTION ---
    if menu == "Recherche Talents" and st.session_state.user_type == "Employeur":
        st.header("Talents disponibles")
        # Simulation d'un profil trouvé
        st.write("Profil Candidat #123")
        if st.button("Sélectionner ce profil 👍"):
            st.session_state.profil_selectionne = True
            st.success("Profil sélectionné.")

    # --- LOGIQUE LEVÉE ANONYMAT ---
    elif menu == "Gestion Entretiens":
        st.header("🤝 Espace Entretiens")
        
        # Le bouton de levée d'anonymat n'apparaît qu'ici avec le pouce
        if not st.session_state.anonymat_leve:
            if st.button("🤝 Lever l'anonymat (Double accord requis) 👍"):
                st.session_state.anonymat_leve = True
                st.rerun()
        else:
            st.success("Anonymat levé. Accès aux documents activé.")
            st.link_button("🎥 Salle Visio Jitsi", "https://meet.jit.si/zipngo-session")
            if st.button("🔄 Retour à l'anonymat"):
                st.session_state.anonymat_leve = False
                st.rerun()

st.markdown(f"--- © {date.today().year} zipngo | .zaxx.app")
