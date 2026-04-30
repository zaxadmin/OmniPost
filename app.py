import streamlit as st
from supabase import create_client, Client

# 1. CONNEXION SUPABASE (Utilise tes secrets Streamlit Cloud)
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("⚠️ Erreur : Les clés Supabase ne sont pas configurées dans les Secrets de Streamlit.")
    st.stop()

st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀", layout="wide")

# --- GESTION DE LA SESSION ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"

# --- INTERFACE AUTHENTIFICATION (LOGIN / SIGNUP) ---
if not st.session_state.auth:
    if st.session_state.auth_mode == "login":
        st.title("🔐 Connexion RH - OmniPost")
        email = st.text_input("Email professionnel")
        pwd = st.text_input("Mot de passe", type="password")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Se connecter"):
                res = supabase.table("profiles").select("*").eq("email", email).eq("password", pwd).execute()
                if len(res.data) > 0:
                    st.session_state.auth = True
                    st.session_state.user = res.data[0]
                    st.rerun()
                else: st.error("Échec de connexion.")
        with col2:
            if st.button("Créer un compte"):
                st.session_state.auth_mode = "signup"
                st.rerun()

    elif st.session_state.auth_mode == "signup":
        st.title("📝 Inscription Nouvel Employeur")
        n_email = st.text_input("Email")
        n_pwd = st.text_input("Mot de passe", type="password")
        n_ent = st.text_input("Nom de l'entreprise")
        if st.button("Valider l'inscription"):
            supabase.table("profiles").insert({"email": n_email, "password": n_pwd, "entreprise": n_ent}).execute()
            st.success("Compte créé ! Connectez-vous.")
            st.session_state.auth_mode = "login"
            st.rerun()
        if st.button("Retour"):
            st.session_state.auth_mode = "login"
            st.rerun()
    st.stop()

# --- TABLEAU DE BORD (SI CONNECTÉ) ---
st.title(f"🚀 OmniPost - {st.session_state.user['entreprise']}")
if st.sidebar.button("Déconnexion"):
    st.session_state.auth = False
    st.rerun()

tab1, tab2, tab3 = st.tabs(["📝 Créer une Offre", "🔑 Mes Comptes", "📁 Candidatures"])

# --- ONGLET 1 : CRÉATION (CLOISONNÉE) ---
with tab1:
    st.header("Nouvelle Annonce")
    titre = st.text_input("Titre du poste")
    if st.button("Publier l'offre"):
        # On injecte l'ID de l'employeur pour que l'offre lui appartienne
        supabase.table("offres").insert({
            "titre": titre, 
            "id_employeur": st.session_state.user['id']
        }).execute()
        st.success("Offre enregistrée dans votre espace privé !")

# --- ONGLET 3 : CANDIDATURES (FILTRÉES) ---
with tab3:
    st.header("Vos Candidats")
    # On ne récupère que les candidats liés aux offres de cet employeur
    data = supabase.table("candidats").select("*, offres!inner(*)").eq("offres.id_employeur", st.session_state.user['id']).execute()
    if data.data:
        for c in data.data:
            st.write(f"👤 {c['nom']} - Score : {c['score']}%")
    else:
        st.write("Aucun candidat pour le moment.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f'<div style="text-align: center; color: #888; font-size: 12px;">Créé par <a href="mailto:rakotobelili63@gmail.com" style="color: #3b82f6;">RAKOTOBE Liliane</a></div>', unsafe_allow_html=True)
