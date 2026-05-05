import streamlit as st
from supabase import create_client

# 1. Configuration de la page
st.set_page_config(page_title="Zax Omnipost - RH & Recrutement", layout="wide", page_icon="📡")

# 2. Connexion Supabase (invisible pour l'utilisateur)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# 3. Gestion de la session de connexion
if 'user' not in st.session_state:
    st.title("📡 Accès Omnipost")
    st.markdown("---")
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("Espace RH & Employeur")
            email = st.text_input("Identifiant (Email)")
            password = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e:
                    st.error("Accès refusé : Identifiants invalides.")
else:
    # --- INTERFACE UNE FOIS CONNECTÉ ---
    
    # Sidebar de navigation
    st.sidebar.title("Zax Omnipost")
    st.sidebar.write(f"Connecté : **{st.session_state.user.email}**")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "Menu Principal", 
        ["Tableau de bord", "Entretien Vidéo (RH)", "Profil & Sécurité"]
    )
    
    if st.sidebar.button("Déconnexion"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()

    # --- SECTION 1 : DASHBOARD ---
    if menu == "Tableau de bord":
        st.header("📊 Dashboard Recrutement")
        st.write("Bienvenue dans votre interface de gestion Omnipost.")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entretiens prévus", "4")
        c2.metric("Nouveaux profils", "12")
        c3.metric("Statut Système", "Opérationnel")

    # --- SECTION 2 : ENTRETIEN VIDÉO (JITSI) ---
    elif menu == "Entretien Vidéo (RH)":
        st.header("📽️ Espace Entretien Vidéo")
        st.info("Cette salle est privée. Partagez le nom de la salle ou le lien avec le candidat.")
        
        # On crée un nom de salle basé sur l'ID de l'employeur pour la confidentialité
        room_id = f"Zax-Entretien-{st.session_state.user.id[:8]}"
        
        col_info, col_link = st.columns([2, 1])
        with col_info:
            st.write(f"**Nom de la salle actuelle :** `{room_id}`")
        with col_link:
            st.link_button("Ouvrir en plein écran", f"https://meet.jit.si/{room_id}")

        # Intégration de la fenêtre Jitsi Meet
        st.components.v1.iframe(
            f"https://meet.jit.si/{room_id}#config.startWithAudioMuted=true&config.startWithVideoMuted=true", 
            height=700, 
            scrolling=False
        )

    # --- SECTION 3 : MON COMPTE ---
    elif menu == "Profil & Sécurité":
        st.header("⚙️ Paramètres du compte")
        st.subheader("Changer le mot de passe")
        new_p = st.text_input("Nouveau mot de passe", type="password")
        if st.button("Enregistrer les modifications"):
            if len(new_p) >= 6:
                supabase.auth.update_user({"password": new_p})
                st.success("Sécurité mise à jour avec succès !")
            else:
                st.error("Le mot de passe doit faire au moins 6 caractères.")
