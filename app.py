import streamlit as st
from datetime import date

# Configuration de la page
st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀", layout="wide")

# Base de données métiers
FICHES_METIERS = ["Conducteur de Travaux", "Chef de Projet IT", "Commercial", "Assistant Logistique", "Autre"]

st.title("🚀 OmniPost : Éditeur d'Offre Professionnelle")
st.write("### Créé par **RAKOTOBE Liliane**")
st.markdown("---")

# --- SECTION 1 : LOCALISATION & CONTRAT (CRITIQUE) ---
st.header("📍 Localisation & Type de poste")
c1, c2, c3 = st.columns(3)

with c1:
    lieu = st.text_input("Ville ou Département", placeholder="ex: Paris (75) ou Télétravail")
    teletravail = st.select_slider(
        "Option Télétravail",
        options=["Présentiel", "1 jour/semaine", "Hybride (50%)", "Full Remote (100%)"]
    )

with c2:
    type_contrat = st.selectbox("Nature du contrat", ["CDI", "CDD", "Alternance", "Intérim", "Stage"])
    date_debut = st.date_input("Date de prise de poste", date.today())

with c3:
    salaire = st.number_input("Rémunération brute annuelle (K€)", 20, 150, 35)
    urgent = st.toggle("🚨 Recrutement Prioritaire / Urgent")

# --- SECTION 2 : PROFIL RECHERCHÉ ---
st.divider()
st.header("👤 Profil & Compétences")
col_a, col_b, col_c = st.columns(3)

with col_a:
    metier = st.selectbox("Métier", ["-- Sélectionner --"] + FICHES_METIERS)
    experience = st.selectbox("Niveau d'expérience", ["Débutant", "1-3 ans", "3-5 ans", "+5 ans"])

with col_b:
    diplome = st.selectbox("Diplôme requis", ["Bac", "Bac+2 (BTS/DUT)", "Bac+3 (Licence)", "Bac+5 (Master)"])
    langues = st.multiselect("Langues étrangères", ["Anglais", "Allemand", "Espagnol", "Italien"])

with col_c:
    permis_b = st.checkbox("Permis B indispensable", value=True)
    caces = st.multiselect("CACES / Habilitations", ["CACES 1", "CACES 3", "CACES 5", "Habilitation Électrique"])

# --- SECTION 3 : DESCRIPTION DES MISSIONS ---
st.divider()
st.header("📝 Descriptif du poste")
description = st.text_area("Missions principales et environnement de travail", 
                           placeholder="Décrivez ici les responsabilités quotidiennes du futur collaborateur...")

# --- SECTION 4 : DIFFUSION ---
st.divider()
platforms = st.multiselect("Canaux de multidiffusion", ["LinkedIn", "Indeed", "Monster", "France Travail", "Hellowork"])

if st.button("🚀 PUBLIER L'ANNONCE"):
    if metier != "-- Sélectionner --" and lieu and platforms:
        st.balloons()
        st.success(f"Annonce pour **{metier}** à **{lieu}** validée !")
        
        # Aperçu récapitulatif pour l'utilisateur
        with st.expander("🔍 Vérifier l'aperçu de l'offre avant envoi"):
            st.write(f"**Lieu :** {lieu} ({teletravail})")
            st.write(f"**Contrat :** {type_contrat} à partir du {date_debut}")
            st.write(f"**Salaire :** {salaire} K€/an")
            st.write(f"**Exigences :** {diplome}, {experience}, Permis B: {'Oui' if permis_b else 'Non'}")
            if description:
                st.info(f"**Détail des missions :**\n{description}")
    else:
        st.error("⚠️ Erreur : Le Métier, la Localisation et au moins une Plateforme sont obligatoires.")
