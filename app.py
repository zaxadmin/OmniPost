import streamlit as st
from supabase import create_client
import google.generativeai as genai

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="OmniPost Premium", layout="wide")

# Initialisation de la session pour la prévisualisation et l'IA
if 'preview_mode' not in st.session_state:
    st.session_state.preview_mode = False
if 'desc_auto' not in st.session_state:
    st.session_state.desc_auto = ""

# Connexion Supabase
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- BARRE LATÉRALE ---
with st.sidebar:
    lang = st.radio("🌐 Langue", ["Français", "English"])
    st.divider()
    st.metric("🎁 Crédits offerts", "3")
    st.caption("Pack Premium activé")

# --- DICTIONNAIRE DE LIENS DIFFUSEURS ---
URLS_DIFFUSEURS = {
    "LinkedIn": "https://www.linkedin.com/talent/post-a-job",
    "Indeed": "https://www.indeed.com/hire",
    "Apec": "https://www.apec.fr/recruteur/deposer-une-offre.html",
    "France Travail": "https://entreprise.francetravail.fr/",
    "Welcome to the Jungle": "https://pro.welcometothejungle.com/",
    "Remote OK": "https://remoteok.com/hire-remote-talent",
    "We Work Remotely": "https://weworkremotely.com/post-a-job"
}

tab1, tab2 = st.tabs(["📝 Créer & Diffuser", "⚙️ Configuration IA"])

# --- ONGLET 2 : CONFIGURATION IA ---
with tab2:
    st.header("🤖 Paramètres du moteur d'intelligence artificielle")
    ia_moteur = st.selectbox("Choisir le modèle", ["Gemini", "GPT-4 (OpenAI)", "Claude (Anthropic)", "Copilot (Azure)"])
    ia_cle = st.text_input("Votre Clé API personnelle", type="password", help="Cette clé reste strictement privée et liée à votre compte.")
    
    if st.button("Enregistrer la configuration"):
        # Sauvegarde simulée dans Supabase (à lier à votre table profiles)
        st.success(f"OmniPost est maintenant configuré avec {ia_moteur}")

# --- ONGLET 1 : FORMULAIRE ET APERÇU ---
with tab1:
    if not st.session_state.preview_mode:
        st.header("Nouveau Poste")
        
        is_remote = st.toggle("🌍 Poste 100% en Télétravail (Remote)")

        with st.form("main_form"):
            col1, col2 = st.columns(2)
            with col1:
                titre = st.text_input("Titre du métier", placeholder="ex: Comptable, Développeur...")
                lieu = st.text_input("Lieu", value="Remote" if is_remote else "Paris", disabled=is_remote)
            with col2:
                contrat = st.selectbox("Type de contrat", ["CDI", "CDD", "Freelance", "Alternance"])
                experience = st.select_slider("Expérience requise", ["Débutant", "1-3 ans", "3-5 ans", "5 ans+"])

            st.divider()
            
            # IA Générateur
            st.subheader("📄 Description de l'offre")
            if st.form_submit_button("✨ Demander à l'IA de rédiger l'annonce"):
                # Simulation de génération (nécessite la configuration Gemini faite précédemment)
                st.session_state.desc_auto = f"Voici une annonce générée pour un poste de {titre}..." 
            
            description = st.text_area("Texte de l'annonce", value=st.session_state.desc_auto, height=250)

            st.divider()
            
            st.subheader("📢 Plateformes de diffusion")
            c1, c2, c3 = st.columns(3)
            with c1:
                diff_gen = st.multiselect("Généralistes", ["LinkedIn", "Indeed", "France Travail"], default=["LinkedIn"])
            with c2:
                diff_prem = st.multiselect("Cadres & Experts", ["Apec", "Welcome to the Jungle"])
            with c3:
                def_rem = ["Remote OK"] if is_remote else []
                diff_rem = st.multiselect("Remote spécialisés", ["Remote OK", "We Work Remotely"], default=def_rem)

            valider = st.form_submit_button("👁️ Voir l'aperçu avant diffusion")
            
            if valider:
                st.session_state.temp_job = {
                    "titre": titre, "lieu": lieu, "contrat": contrat, 
                    "exp": experience, "desc": description,
                    "sites": diff_gen + diff_prem + diff_rem
                }
                st.session_state.preview_mode = True
                st.rerun()

    # --- ÉTAPE DE VUE FINALE (PREVIEW) ---
    else:
        job = st.session_state.temp_job
        st.header("👁️ Validation finale")
        st.warning("Relisez attentivement l'annonce ci-dessous avant de confirmer la publication.")

        with st.container(border=True):
            st.title(job['titre'])
            st.caption(f"📍 {job['lieu']} | 📄 {job['contrat']} | 🎓 Expérience : {job['exp']}")
            st.markdown("---")
            st.markdown(job['desc'])
            st.markdown("---")
            st.write("**Diffuseurs sélectionnés :**")
            # Affichage des badges pour chaque site
            st.write(", ".join([f"**{site}**" for site in job['sites']]))

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            if st.button("✅ Valider et Générer les liens de diffusion"):
                st.success("🎉 Annonce validée ! Cliquez sur les liens ci-dessous pour finaliser le dépôt sur chaque site.")
                st.session_state.job_valide = True
        with col_v2:
            if st.button("⬅️ Retour pour modifier"):
                st.session_state.preview_mode = False
                st.rerun()

        # AFFICHAGE DES LIENS DIRECTS APRÈS VALIDATION
        if st.session_state.get('job_valide'):
            st.divider()
            st.subheader("🔗 Vos liens de publication directs :")
            cols = st.columns(len(job['sites']))
            for i, site in enumerate(job['sites']):
                with cols[i]:
                    st.link_button(f"Publier sur {site}", URLS_DIFFUSEURS.get(site, "#"))

