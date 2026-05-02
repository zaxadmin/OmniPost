import streamlit as st
from supabase import create_client, Client

# 1. CONNEXION SUPABASE
try:
    # Ces clés doivent être dans Settings > Secrets sur Streamlit Cloud
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Erreur de configuration : Vérifiez les Secrets Streamlit.")
    st.stop()

st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀", layout="wide")

# --- GESTION DE LA SESSION ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = "login"

# --- INTERFACE AUTHENTIFICATION (ÉTANCHE) ---
if not st.session_state.auth:
    if st.session_state.auth_mode == "login":
        st.title("🔐 Connexion RH - OmniPost")
        email = st.text_input("Email professionnel")
        pwd = st.text_input("Mot de passe", type="password")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Se connecter"):
                # On vérifie dans la table 'profiles'
                res = supabase.table("profiles").select("*").eq("email", email).eq("password", pwd).execute()
                if len(res.data) > 0:
                    st.session_state.auth = True
                    st.session_state.user = res.data[0] # On stocke tout le profil (id, entreprise, etc.)
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
                # Création du profil unique dans Supabase
                supabase.table("profiles").insert({
                    "email": n_email, 
                    "password": n_pwd, 
                    "entreprise": n_ent
                }).execute()
                st.success("Compte créé avec succès ! Connectez-vous.")
                st.session_state.auth_mode = "login"
                st.rerun()
            else:
                st.warning("Veuillez remplir tous les champs.")
        
        if st.button("Retour"):
            st.session_state.auth_mode = "login"
            st.rerun()
    st.stop()

# --- TABLEAU DE BORD (SI CONNECTÉ) ---
st.sidebar.title(f"🏢 {st.session_state.user['entreprise']}")
st.sidebar.write(f"ID Client : `{st.session_state.user['id'][:8]}...`")

if st.sidebar.button("Déconnexion"):
    st.session_state.auth = False
    st.rerun()

st.title(f"🚀 Dashboard OmniPost")

tab1, tab2, tab3 = st.tabs(["📝 Créer une Offre", "🔑 Mes Comptes", "📁 Candidatures"])

# --- ONGLET 1 : CRÉATION (CLOISONNÉE PAR ID) ---
with tab1:
    st.header("Nouvelle Annonce")
    with st.container():
        titre = st.text_input("Titre du poste", placeholder="ex: Ingénieur DevOps")
        lieu = st.text_input("Localisation", placeholder="ex: Paris / Remote")
        col_a, col_b = st.columns(2)
        with col_a:
            contrat = st.selectbox("Contrat", ["CDI", "CDD", "Alternance"])
        with col_b:
            salaire = st.number_input("Salaire (K€)", value=40)
            
        if st.button("🚀 Publier l'offre"):
            if titre:
                # On force l'id_employeur pour que l'offre soit invisible pour les autres
                supabase.table("offres").insert({
                    "titre": titre, 
                    "lieu": lieu,
                    "contrat": contrat,
                    "salaire": salaire,
                    "id_employeur": st.session_state.user['id']
                }).execute()
                st.balloons()
                st.success("Offre enregistrée dans votre espace sécurisé !")
            else:
                st.error("Le titre est obligatoire.")

# --- ONGLET 2 : COMPTES (PERSONNELS) ---
with tab2:
    st.header("Configurations des diffuseurs")
    st.info("Ces clés sont utilisées pour vos propres comptes LinkedIn/Indeed.")
    st.text_input("Clé API LinkedIn (Personnel)", type="password")
    st.text_input("Clé API Indeed (Personnel)", type="password")

# --- ONGLET 3 : CANDIDATURES (FILTRÉES PAR EMPLOYEUR) ---
with tab3:
    st.header("Vos Candidats")
    # On utilise une jointure pour ne voir que les candidats liés aux offres de CET employeur
    data = supabase.table("candidats").select("*, offres!inner(*)").eq("offres.id_employeur", st.session_state.user['id']).execute()
    
    if data.data:
        for c in data.data:
            with st.expander(f"👤 {c['nom']} - Match : {c['score']}%"):
                st.write(f"**Poste :** {c['offres']['titre']}")
                st.write(f"**Analyse IA :** {c.get('analyse_ia', 'En cours...')}")
                st.button(f"Contacter {c['nom']}", key=f"btn_{c['id']}")
    else:
        st.write("Aucune candidature reçue pour vos offres.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f'<div style="text-align: center; color: #888; font-size: 12px;">OmniPost App | Propriété de {st.session_state.user['entreprise']} | Support : <a href="mailto:rakotobelili63@gmail.com" style="color: #3b82f6;">RAKOTOBE Liliane</a></div>', unsafe_allow_html=True)
