import streamlit as st
from supabase import create_client
import google.generativeai as genai

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="OmniPost Premium", layout="wide", page_icon="🚀")

# Connexion Supabase (Utilise tes secrets Streamlit Cloud)
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Erreur de connexion à la base de données.")

# Initialisation des variables de session
if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = False
if 'desc_auto' not in st.session_state:
    st.session_state.desc_auto = ""
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# --- DICTIONNAIRE DES LIENS DIFFUSEURS ---
URLS_DIFFUSEURS = {
    "LinkedIn": "https://www.linkedin.com/talent/post-a-job",
    "Indeed": "https://www.indeed.com/hire",
    "Apec": "https://www.apec.fr/recruteur/deposer-une-offre.html",
    "France Travail": "https://entreprise.francetravail.fr/",
    "Welcome to the Jungle": "https://pro.welcometothejungle.com/",
    "Remote OK": "https://remoteok.com/hire-remote-talent",
    "We Work Remotely": "https://weworkremotely.com/post-a-job"
}

# --- LOGIQUE DE SÉCURITÉ & LICENCE ---
def verifier_droits_utilisateur():
    """Vérifie si l'utilisateur peut utiliser l'IA (Licence ou Essai)."""
    # Simulation d'ID utilisateur (à lier à ton système d'auth)
    user_id = st.session_state.get('user_id', 'default_user') 
    
    try:
        res = supabase.table("profiles").select("a_achete_licence, essais_utilises, ia_api_key").eq("id", user_id).single().execute()
        return res.data
    except:
        return {"a_achete_licence": False, "essais_utilises": 0, "ia_api_key": None}

def generer_texte_ia(prompt_text, profil):
    """Génère l'annonce en respectant les quotas et les clés."""
    # 1. Priorité à la clé personnelle du client
    if profil.get('ia_api_key'):
        try:
            genai.configure(api_key=profil['ia_api_key'])
            model = genai.GenerativeModel('gemini-pro')
            return model.generate_content(prompt_text).text
        except:
            st.error("Erreur avec votre clé personnelle.")
            return None
    
    # 2. Utilisation de ta clé (Limitée à 3 clics par session pour éviter les abus)
    if st.session_state.usage_count >= 3:
        st.warning("⚠️ Limite d'utilisation de notre clé atteinte. Ajoutez la vôtre en paramètres !")
        return None
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        st.session_state.usage_count += 1
        return model.generate_content(prompt_text).text
    except:
        st.error("Service IA indisponible actuellement.")
        return None

# --- INTERFACE ---
tab1, tab2 = st.tabs(["📝 Créer & Diffuser", "⚙️ Paramètres & Licence"])

# Récupération des infos du profil
profil = verifier_droits_utilisateur()

# --- ONGLET 2 : PARAMÈTRES & LICENCE ---
with tab2:
    st.header("⚙️ Votre Compte")
    
    # Section Licence
    if profil['a_achete_licence']:
        st.success("✅ Votre licence Premium est active.")
    else:
        st.warning(f"🎁 Mode Essai : {1 - profil['essais_utilises']} annonce gratuite restante.")
        if st.button("💳 Acheter la licence illimitée"):
            st.info("Redirection vers le paiement...")

    st.divider()
    
    # Section Clé API
    st.subheader("🤖 Votre propre intelligence artificielle")
    cle_saisie = st.text_input("Clé Google Gemini (Optionnel)", type="password", value=profil.get('ia_api_key', ""))
    if st.button("Sauvegarder ma clé"):
        supabase.table("profiles").update({"ia_api_key": cle_saisie}).eq("id", st.session_state.get('user_id')).execute()
        st.success("Clé enregistrée !")

# --- ONGLET 1 : FORMULAIRE & DIFFUSION ---
with tab1:
    # Blocage si essai terminé et pas de licence
    if not profil['a_achete_licence'] and profil['essais_utilises'] >= 1:
        st.error("🚀 Votre essai gratuit est terminé. Veuillez acheter une licence pour continuer.")
    
    elif not st.session_state.preview_mode:
        st.header("Nouvelle Offre d'Emploi")
        is_remote = st.toggle("🌍 Poste 100% Remote")

        with st.form("main_form"):
            col1, col2 = st.columns(2)
            with col1:
                titre = st.text_input("Titre du poste", placeholder="ex: Chef de Projet")
                lieu = st.text_input("Localisation", value="Remote" if is_remote else "Paris", disabled=is_remote)
            with col2:
                contrat = st.selectbox("Type de contrat", ["CDI", "CDD", "Freelance", "Stage"])
                exp = st.select_slider("Expérience", ["Débutant", "1-3 ans", "3-5 ans", "5 ans+"])

            st.divider()
            
            # Action IA
            if st.form_submit_button("✨ Générer l'annonce avec l'IA"):
                p = f"Rédige une offre d'emploi attractive pour un {titre} en {contrat} à {lieu}. Expérience : {exp}."
                res = generer_texte_ia(p, profil)
                if res:
                    st.session_state.desc_auto = res

            description = st.text_area("Texte de l'offre", value=st.session_state.desc_auto, height=300)

            st.subheader("📢 Choix des diffuseurs")
            d_gen = st.multiselect("Généralistes", ["LinkedIn", "Indeed", "France Travail"], default=["LinkedIn"])
            d_prem = st.multiselect("Premium / Cadres", ["Apec", "Welcome to the Jungle"])
            d_rem = st.multiselect("Remote", ["Remote OK", "We Work Remotely"])

            if st.form_submit_button("👁️ Voir l'aperçu avant diffusion"):
                if titre and description:
                    st.session_state.temp_job = {
                        "titre": titre, "lieu": lieu, "contrat": contrat, 
                        "exp": exp, "desc": description,
                        "sites": d_gen + d_prem + d_rem
                    }
                    st.session_state.preview_mode = True
                    st.rerun()
                else:
                    st.error("Titre et description requis.")

    # --- MODE APERÇU ---
    else:
        job = st.session_state.temp_job
        st.header("👁️ Aperçu final")
        with st.container(border=True):
            st.title(job['titre'])
            st.write(f"📍 {job['lieu']} | {job['contrat']} | Expérience : {job['exp']}")
            st.markdown("---")
            st.markdown(job['desc'])

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            if st.button("✅ Confirmer et Publier"):
                # Sauvegarde Supabase
                supabase.table("offres").insert({
                    "titre": job['titre'], "description": job['desc'], 
                    "lieu": job['lieu'], "diffuseurs": ", ".join(job['sites'])
                }).execute()
                
                # Mise à jour du compteur d'essais (si pas de licence)
                if not profil['a_achete_licence']:
                    supabase.table("profiles").update({"essais_utilises": 1}).eq("id", st.session_state.get('user_id')).execute()
                
                st.session_state.job_done = True
                st.success("Annonce validée !")
        with col_v2:
            if st.button("⬅️ Retour"):
                st.session_state.preview_mode = False
                st.rerun()

        if st.session_state.get('job_done'):
            st.divider()
            st.subheader("🔗 Liens directs pour publier :")
            cols = st.columns(len(job['sites']))
            for i, site in enumerate(job['sites']):
                with cols[i]:
                    st.link_button(f"Aller sur {site}", URLS_DIFFUSEURS.get(site, "#"))
