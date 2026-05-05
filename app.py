import streamlit as st
from supabase import create_client

st.set_page_config(page_title="ZAXX Omnipost", layout="wide", page_icon="📡")

# Connexion à la base ZAXX
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #3b82f6; font-weight: 900; font-style: italic;'>ZAXX OMNIPOST</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: 800; letter-spacing: 2px; color: #64748b;'>POLE OPÉRATIONNEL & RH</p>", unsafe_allow_html=True)
    st.divider()
    
    with st.container():
        email = st.text_input("Identifiant Direction")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("AUTHENTIFICATION ZAXX", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.success("Connexion établie.")
                st.rerun()
            except:
                st.error("Accès refusé par le système ZAXX.")
else:
    st.sidebar.markdown("<h2 style='color: #3b82f6; font-weight: 900;'>ZAXX OP</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Navigation", ["Vue Ensemble", "Entretien Visio", "Paramètres"])
    
    if menu == "Vue Ensemble":
        st.header("🏢 Pilotage des Ressources")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Sièges ZAXX Total", "Illimité")
        with col2:
            st.metric("Recrutements en cours", 8)
        st.info("Interface sécurisée ZAXX OMNIPOST.")

    elif menu == "Entretien Visio":
        st.header("📽️ Studio d'Entretien ZAXX")
        room = f"ZAXX-OP-{st.session_state.user.id[:8]}"
        st.code(f"Lien à transmettre : https://meet.jit.si/{room}", language="markdown")
        st.components.v1.iframe(f"https://meet.jit.si/{room}", height=750)

    elif menu == "Paramètres":
        st.header("⚙️ Sécurité du Compte")
        if st.button("Demander réinitialisation mot de passe"):
            st.warning("Contactez l'administrateur ZAXX COMMANDO.")

    if st.sidebar.button("FERMER LA SESSION"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()
