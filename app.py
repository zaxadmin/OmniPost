import streamlit as st
from supabase import create_client

# Setup
st.set_page_config(page_title="Zax Omnipost", layout="wide", page_icon="📡")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.title("📡 Zax Omnipost")
    st.subheader("Portail Recrutement & RH")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Connexion Direction", use_container_width=True):
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = res.user
        st.rerun()
else:
    st.sidebar.title("Zax Omnipost")
    menu = st.sidebar.radio("Menu", ["Dashboard", "Entretien Vidéo", "Sécurité"])
    
    if menu == "Dashboard":
        st.header("🏢 Suivi des Recrutements")
        st.metric("Entretiens prévus cette semaine", 5)
        st.info("Interface optimisée pour la Direction RH.")

    elif menu == "Entretien Vidéo":
        st.header("📽️ Salle d'entretien")
        room = f"Zax-Omni-{st.session_state.user.id[:8]}"
        st.components.v1.iframe(f"https://meet.jit.si/{room}", height=700)

    elif menu == "Sécurité":
        st.header("⚙️ Compte")
        new_p = st.text_input("Changer le mot de passe", type="password")
        if st.button("Confirmer"):
            supabase.auth.update_user({"password": new_p})
            st.success("Accès mis à jour.")

    if st.sidebar.button("Quitter"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()
