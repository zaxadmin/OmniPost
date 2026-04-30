import streamlit as st

# Configuration de la page
st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀")

# Style CSS pour améliorer le visuel
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        height: 3em;
    }
    </style>
    """, unsafe_allow_stdio=True)

# En-tête
st.title("🚀 OmniPost")
st.write("### Créé par **RAKOTOBE Liliane**")
st.markdown("---")

# Barre latérale pour les options
with st.sidebar:
    st.header("Paramètres / Settings")
    lang = st.radio("Langue de l'interface", ["Français", "English"])
    st.divider()
    st.info("Version 1.1.0 - Bilingue Ready")

# Textes selon la langue
if lang == "Français":
    t_config = "⚙️ Configuration du flux"
    t_email = "Email de réception des candidatures"
    t_job_section = "📝 Détails de l'offre"
    t_job_title = "Intitulé du poste (ex: Chef de projet)"
    t_platforms = "Diffuser sur ces plateformes :"
    t_btn = "Lancer la multidiffusion 1-Clic"
    t_success = "🚀 Offre diffusée avec succès sur tous les canaux !"
else:
    t_config = "⚙️ Stream Configuration"
    t_email = "Candidate reception email"
    t_job_section = "📝 Job Details"
    t_job_title = "Job Title (e.g. Project Manager)"
    t_platforms = "Post on these platforms:"
    t_btn = "Launch 1-Click Broadcast"
    t_success = "🚀 Job successfully posted on all channels!"

# Section 1 : Configuration
st.header(t_config)
email = st.text_input(t_email, value="contact@entreprise.com")

st.divider()

# Section 2 : L'Offre
st.header(t_job_section)
col1, col2 = st.columns(2)

with col1:
    job = st.text_input(t_job_title)
with col2:
    category = st.selectbox("Catégorie", ["BTP", "Informatique", "Commerce", "Santé"])

platforms = st.multiselect(
    t_platforms, 
    ["LinkedIn", "Indeed", "Monster", "Glassdoor", "France Travail", "Agences Intérim"]
)

# Section Action
st.markdown("###")
if st.button(t_btn):
    if job and platforms:
        st.balloons()
        st.success(t_success)
        st.json({
            "status": "Active",
            "job": job,
            "distributed_to": platforms,
            "owner": "RAKOTOBE Liliane"
        })
    else:
        st.error("Veuillez remplir le titre et choisir au moins une plateforme.")
