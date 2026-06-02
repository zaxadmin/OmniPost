import streamlit as st, pandas as pd, io, json
from supabase import create_client
from groq import Groq
from pypdf import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | Plateforme Professionnelle", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- UI PRINCIPALE ---
st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🚀 Bienvenue sur zipngo")
    st.write("Votre plateforme de mise en relation professionnelle.")
    st.divider()
    role = st.radio("Accès :", ["Candidat", "Employeur"])

# --- ESPACE CANDIDAT ---
if role == "Candidat":
    st.subheader("👤 Espace Candidat")
    with st.expander("📖 Mode d'emploi"):
        st.write("1. Déposez votre CV. 2. Indiquez le poste. 3. Gérez vos candidatures. Accès gratuit 3 mois.")
    
    cv_file = st.file_uploader("Document obligatoire : Déposez votre CV (PDF)", type=["pdf"])
    if cv_file:
        tab1, tab2 = st.tabs(["Optimisation de parcours", "Suivi & Entretien"])
        with tab1:
            poste = st.text_input("Poste visé")
            if st.button("Valider"): st.success("Analyse en cours.")
    else:
        st.warning("⚠️ Le dépôt du CV est requis pour accéder aux fonctionnalités.")

# --- ESPACE EMPLOYEUR ---
elif role == "Employeur":
    st.subheader("💼 Espace Employeur")
    with st.expander("📖 Mode d'emploi"):
        st.write("1. Renseignez l'entreprise. 2. Créez l'offre. 3. Recevez les profils correspondants.")
    
    with st.form("form_employeur"):
        col1, col2 = st.columns(2)
        entreprise = col1.text_input("Nom de l'entreprise")
        contact_nom = col2.text_input("Nom et prénom")
        email = col1.text_input("Email de contact")
        tel = col2.text_input("Téléphone")
        
        poste = col1.text_input("Intitulé du poste")
        duree = col2.selectbox("Type de contrat", ["CDI", "CDD", "Alternance", "Stage", "Intérim"])
        horaire = col1.selectbox("Organisation horaire", ["Fixe", "2x8", "3x8", "Variable"])
        ville = col2.text_input("Ville")
        
        exigences = st.multiselect("Prérequis", ["Diplôme", "Permis", "Langues"])
        salaire = st.number_input("Salaire proposé")
        
        if st.form_submit_button("Valider et Créer l'offre"):
            st.success(f"Offre pour {poste} créée. Transmission aux profils correspondants en cours.")

# --- CONDITIONS ET PREMIUM ---
st.markdown("---")
if st.checkbox("J'accepte les conditions d'utilisation"):
    st.markdown("""
    **Rappel des limites :**
    - **Gratuité :** 3 mois d'accès (profil mis en veille ensuite).
    - **Candidat :** Optimisation et tri : 1 fois/mois | Prospection : 20 messages/mois.
    - **Employeur :** Diffusion : 1 fois | Tri candidatures : 1 fois/mois.
    """)
    c1, c2 = st.columns(2)
    with c1: st.link_button("Pass Premium Candidat (6€)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    with c2: st.link_button("Pass Premium Recruteur (39€)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

st.markdown("<div style='text-align: center; margin-top: 20px;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
