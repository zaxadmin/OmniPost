import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Zax Omnipost", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

if 'user' not in st.session_state:
    st.title("📡 Accès Omnipost")
    e = st.text_input("Email")
    p = st.text_input("Pass", type="password")
    if st.button("Entrer"):
        res = supabase.auth.sign_in_with_password({"email": e, "password": p})
        st.session_state.user = res.user
        st.rerun()
else:
    menu = st.sidebar.radio("Zax Menu", ["Dashboard", "Vidéoconférence", "Mon Compte"])
    
    if menu == "Vidéoconférence":
        st.header("📽 Salon Privé")
        room = f"ZaxOmni-{st.session_state.user.id[:8]}"
        st.components.v1.iframe(f"https://meet.jit.si/{room}", height=600)
        
    if menu == "Mon Compte":
        st.header("⚙️ Paramètres")
        new_p = st.text_input("Nouveau MDP", type="password")
        if st.button("Mettre à jour"):
            supabase.auth.update_user({"password": new_p})
            st.success("C'est fait !")
