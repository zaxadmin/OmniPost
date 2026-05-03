import streamlit as st
from supabase import create_client
import google.generativeai as genai

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="OmniPost Premium", layout="wide", page_icon="🚀")

# Connexion Supabase
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Connexion à la base de données impossible. Vérifiez vos secrets.")

# Initialisation de la session
if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = False
if 'desc_auto' not in st.session_state:
    st.session_state.desc_auto = ""
if 'finalise' not in st.session_state:
    st.session_state.finalise = False

# --- LIENS DIFFUSEURS ---
URLS_DIFFUSEURS = {
    "LinkedIn": "https://www.linkedin.com/talent/post-a-job",
    "Indeed": "https://www.indeed.com/hire",
    "Apec": "https://www.apec.fr/recruteur/deposer-une-offre.html",
    "France Travail": "https://entreprise.francetravail.fr/",
    "Welcome to the Jungle": "https://pro.welcometothejungle.com/",
    "Remote OK": "https://remoteok.com/hire-remote-talent"
}

# --- LOGIQUE IA SÉCURISÉE ---
def generer_ia(prompt, profil):
    cle_client = profil.get('ia_api_key')
    
    # 1. Clé du client (Priorité - Gratuit pour toi)
    if cle_client:
        try:
            genai.configure(api_key=cle_client)
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model.generate_content(prompt).text
        except Exception as e:
            st.error(f"Erreur avec votre clé personnelle : {e}")
            return None
            
    # 2. Ta clé (Essai unique - Coût infime pour toi)
    elif profil.get('essais_utilises', 0) < 1:
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model.generate_content(prompt).text
        except:
            st.error("Le service d'essai est saturé. Réessayez avec votre propre clé.")
            return None
    else:
        return "BLOCKED"

# --- INTERFACE ---
tab1, tab2 = st.tabs(["📝 Créer une annonce", "⚙️ Mon Compte & IA"])

# Récupération profil (Exemple avec l'ID session)
user_id = st.session_state.get('user_id', 'user_id_fixe') # À lier à ton Auth
res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
profil = res.data

# --- ONGLET 2 : COMPTE ET GUIDE CLÉ API ---
with tab2:
    st.header("⚙️ Paramètres & Licence")
    
    if profil['a_achete_licence']:
        st.success("✅ Licence Illimitée Active")
    else:
        st.warning(f"🎁 Essai gratuit : {1 - profil['essais_utilises']} restant")

    st.divider()

    st.subheader("🤖 Votre Intelligence Artificielle")
    st.write("OmniPost fonctionne sans abonnement grâce à l'utilisation de votre propre clé API.")
    
    with st.expander("🔑 Comment obtenir ma clé Gemini gratuite ?"):
        st.markdown("""
        1. Allez sur **[Google AI Studio](https://aistudio.google.com/)**.
        2. Cliquez sur **'Get API key'** à gauche.
        3. Cliquez sur **'Create API key in new project'**.
        4. Copiez la clé (`AIza...`) et collez-la ici.
        """)
    
    cle_saisie = st.text_input("Collez votre clé API ici", type="password", value=profil.get('ia_api_key', ""))
    if st.button("Enregistrer ma configuration"):
        supabase.table("profiles").update({"ia_api_key": cle_saisie}).eq("id", user_id).execute()
        st.success("Clé enregistrée avec succès !")

# --- ONGLET 1 : RÉDACTION ---
with tab1:
    # CAS : ESSAI FINI ET PAS DE LICENCE
    if not profil['a_achete_licence'] and profil['essais_utilises'] >= 1:
        st.header("🚀 Continuez l'aventure OmniPost")
        st.info("Votre essai gratuit est terminé. Débloquez l'outil à vie pour le prix d'un café.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Pourquoi prendre la licence ?")
            st.write("- ✅ Annonces illimitées")
