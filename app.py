import streamlit as st

st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀")

# Barre latérale pour la langue
lang = st.sidebar.radio("Langue / Language", ["Français", "English"])

# Titre principal
st.title("🚀 OmniPost")
st.write(f"Créé par **RAKOTOBE Liliane**")

# Section 1 : Configuration du compte
st.header("1. Configuration" if lang == "Français" else "1. Setup")
email_col1, email_col2 = st.columns([3, 1])
with email_col1:
    current_email = st.text_input("Email de réception", "contact@entreprise.com")
with email_col2:
    if st.button("Changer" if lang == "Français" else "Change"):
        st.success("Compte mis à jour !" if lang == "Français" else "Account updated!")

# Section 2 : Diffusion de l'offre
st.header("2. Diffusion" if lang == "Français" else "2. Broadcasting")
job_title = st.text_input("Titre du poste" if lang == "Français" else "Job Title")
platforms = st.multiselect(
    "Choisir les plateformes" if lang == "Français" else "Select Platforms",
    ["LinkedIn", "Indeed", "Monster", "Glassdoor", "France Travail", "Agencies"]
)

if st.button("Lancer la multidiffusion 1-Clic" if lang == "Français" else "Launch 1-Click Broadcast"):
    if job_title and platforms:
        st.balloons()
        st.success("🚀 Offre diffusée avec succès !" if lang == "Français" else "🚀 Job posted successfully!")
    else:
        st.error("Veuillez remplir tous les champs" if lang == "Français" else "Please fill all fields")
