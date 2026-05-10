import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Zaxx Login", page_icon="🔐")

# Connexion à Supabase "zip"
supabase = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])

st.title("🛡️ Portail Zaxx.app")

tab1, tab2 = st.tabs(["Connexion", "Création de compte"])

with tab2:
    st.subheader("Rejoindre la plateforme")
    new_email = st.text_input("Email", key="reg_email")
    new_pwd = st.text_input("Mot de passe", type="password", key="reg_pwd")
    user_role = st.radio("Vous êtes :", ["Candidat", "Employeur"])
    
    if st.button("S'inscrire"):
        try:
            supabase.table("users").insert({"email": new_email, "password": new_pwd, "role": user_role}).execute()
            st.success("Compte créé ! Connectez-vous maintenant.")
        except:
            st.error("Erreur lors de l'inscription (l'utilisateur existe peut-être déjà).")

with tab1:
    st.subheader("Accès sécurisé")
    email = st.text_input("Email", key="log_email")
    pwd = st.text_input("Mot de passe", type="password", key="log_pwd")
    
    if st.button("Entrer"):
        user = supabase.table("users").select("*").eq("email", email).eq("password", pwd).execute()
        if user.data:
            role = user.data[0]['role']
            base_url = "https://zax-omnipost.streamlit.app"
            # Redirection propre avec passage de paramètres
            target = f"{base_url}/?view=candidat&user={email}" if role == "Candidat" else base_url
            st.markdown(f'<a href="{target}" target="_self" style="display:inline-block; padding:12px 25px; background:#00467F; color:white; border-radius:8px; text-decoration:none; font-weight:bold;">🚀 Accéder à OmniPost</a>', unsafe_allow_html=True)
        else:
            st.error("Identifiants invalides.")
