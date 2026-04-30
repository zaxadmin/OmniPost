import streamlit as st
from datetime import date

# Configuration de la page
st.set_page_config(page_title="OmniPost - Rakotobe Liliane", page_icon="🚀", layout="wide")

# Base de données métiers
FICHES_METIERS = ["Conducteur de Travaux", "Chef de Projet IT", "Commercial", "Assistant Logistique", "Autre"]

st.title("🚀 OmniPost : Éditeur d'Offre Professionnelle")
st.markdown("---")

# --- SECTION 1 : LOCALISATION & CONTRAT ---
st.header("📍 Localisation & Type de poste")
c1, c2, c3 = st.columns(3)

with c1:
    lieu = st.text_input("Ville ou Département", placeholder="ex: Paris (75)")
    teletravail = st.select_slider(
        "Option Télétravail",
        options=["Présentiel", "1 jour/semaine", "Hybride (50%)", "Full Remote (100%)"]
    )

with c2:
    type_contrat = st.selectbox("Nature du contrat", ["CDI", "CDD", "Alternance", "Intérim", "Stage"])
    date_debut = st.date_input("Date de prise de poste", date.today())

with c3:
    salaire = st.number_input("Rémunération brute annuelle (K€)", 20, 150, 35)
    urgent = st.toggle("🚨 Recrutement Prioritaire")

# --- SECTION 2 : PROFIL RECHERCHÉ ---
st.divider()
st.header("👤 Profil & Compétences")
col_a, col_b, col_c = st.columns(3)

with col_a:
    metier = st.selectbox("Métier", ["-- Sélectionner --"] + FICHES_METIERS)
    experience = st.selectbox("Niveau d'expérience", ["Débutant", "1-3 ans", "3-5 ans", "+5 ans"])

with col_b:
    diplome = st.selectbox("Diplôme requis", ["Bac", "Bac+2", "Bac+3", "Bac+5"])
    langues = st.multiselect("Langues étrangères", ["Anglais", "Allemand", "Espagnol", "Italien"])

with col_c:
    permis_b = st.checkbox("Permis B indispensable", value=True)
    caces = st.multiselect("CACES / Habilitations", ["CACES 1", "CACES 3", "CACES 5", "Habilitation Électrique"])

# --- SECTION 3 : DESCRIPTION ---
st.divider()
st.header("📝 Descriptif du poste")
description = st.text_area("Missions principales", placeholder="Décrivez ici les responsabilités...")

# --- SECTION 4 : DIFFUSION ---
st.divider()
platforms = st.multiselect("Canaux de multidiffusion", ["LinkedIn", "Indeed", "Monster", "France Travail", "Hellowork"])

if st.button("🚀 PUBLIER L'ANNONCE"):
    if metier != "-- Sélectionner --" and lieu and platforms:
        st.balloons()
        st.success(f"Annonce pour **{metier}** validée !")
    else:
        st.error("⚠️ Erreur : Le Métier, la Localisation et les Plateformes sont obligatoires.")

# --- FOOTER (BAS DE PAGE) ---
st.markdown("---")
footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #888888;
        text-align: center;
        font-size: 12px;
        padding: 10px;
    }
    .footer a {
        color: #3b82f6;
        text-decoration: none;
    }
    </style>
    <div class="footer">
        <p>Créé par <a href="mailto:rakotobelili63@gmail.com">RAKOTOBE Liliane</a></p>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)
