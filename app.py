import streamlit as st
from supabase import create_client, Client

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀", layout="wide")

# --- 2. CONNEXION SUPABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("⚠️ Erreur : Les 'Secrets' ne sont pas configurés sur Streamlit Cloud.")
        st.stop()

supabase = init_connection()

# --- 3. GESTION DE LA SESSION ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"

# --- 4. INTERFACE AUTHENTIFICATION ---
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
                else:
                    st.error("Identifiants incorrects.")
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
            if n_email and n_pwd and n_ent:
                supabase.table("profiles").insert({
                    "email": n_email, 
                    "password": n_pwd, 
                    "entreprise": n_ent
                }).execute()
                st.success("Compte créé ! Connectez-vous.")
                st.session_state.auth_mode = "login"
                st.rerun()
            else:
                st.warning("Veuillez remplir tous les champs.")
        
        if st.button("Retour"):
            st.session_state.auth_mode = "login"
            st.rerun()
    st.stop()

# --- 5. TABLEAU DE BORD (SI CONNECTÉ) ---
st.sidebar.title(f"🏢 {st.session_state.user['entreprise']}")
st.sidebar.write(f"ID : `{st.session_state.user['id'][:8]}`")

if st.sidebar.button("Déconnexion"):
    st.session_state.auth = False
    st.rerun()

st.title(f"🚀 Dashboard OmniPost")
tab1, tab2, tab3 = st.tabs(["📝 Créer une Offre", "🔑 Mes Comptes", "📁 Candidatures"])

# --- ONGLET 1 : CRÉATION ---
with tab1:
    st.header("Nouvelle Annonce")
    titre = st.text_input("Titre du poste", placeholder="ex: Ingénieur DevOps")
    lieu = st.text_input("Localisation", placeholder="ex: Paris / Remote")
    col_a, col_b = st.columns(2)
    with col_a:
        contrat = st.selectbox("Contrat", ["CDI", "CDD", "Alternance"])
    with col_b:
        salaire = st.number_input("Salaire (K€)", value=40)
            
    if st.button("🚀 Publier l'offre"):
        if titre:
            supabase.table("offres").insert({
                "titre": titre, 
                "lieu": lieu,
                "contrat": contrat,
                "salaire": salaire,
                "id_employeur": st.session_state.user['id']
            }).execute()
            st.balloons()
            st.success("Offre publiée !")
        else:
            st.error("Le titre est obligatoire.")

# --- ONGLET 2 : COMPTES ---
with tab2:
    st.header("Configurations")
    st.info("Paramétrez vos accès diffuseurs.")
    st.text_input("Clé API LinkedIn", type="password")
    st.text_input("Clé API Indeed", type="password")

# --- ONGLET 3 : CANDIDATURES ---
with tab3:
    st.header("Vos Candidats")
    data = supabase.table("candidats").select("*, offres!inner(*)").eq("offres.id_employeur", st.session_state.user['id']).execute()
    
    if data.data:
        for c in data.data:
            with st.expander(f"👤 {c['nom']} - Match : {c['score']}%"):
                st.write(f"**Poste :** {c['offres']['titre']}")
                st.button(f"Contacter", key=f"btn_{c['id']}")
    else:
        st.write("Aucune candidature.")

# --- FOOTER ---
st.markdown("---")
# Correction de la syntaxe des guillemets ici :
footer_html = f"""
<div style="text-align: center; color: #888; font-size: 12px;">
    OmniPost App | Propriété de {st.session_state.user['entreprise']} | 
    Support : <a href="mailto:rakotobelili63@gmail.com" style="color: #3b82f6;">RAKOTOBE Liliane</a>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
