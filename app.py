import streamlit as st
import re
from groq import Groq
from supabase import create_client
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- FONCTIONS ---
def moteur_ia(prompt):
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192", max_tokens=1000)
        return res.choices[0].message.content
    except Exception as e: return f"Erreur : {e}"

def creer_salle_jitsi(id_candidature):
    return f"https://meet.jit.si/zipngo-{id_candidature}"

# --- TEXTES ---
TEXTES = {
    "presentation": "### 🚀 Bienvenue sur Zipngo, l'accélérateur de carrière international.",
    "cgv": "**CONDITIONS GÉNÉRALES :**\n1. Outil de mise en relation.\n2. Traitement des données par IA.\n3. Contact : creationsites06@gmail.com"
}

# --- AUTHENTIFICATION ---
if "role" not in st.session_state:
    st.title("Zipngo")
    st.markdown(TEXTES["presentation"])
    st.sidebar.title("Connexion / Création")
    st.session_state.role = st.sidebar.radio("Je suis un :", ["Candidat", "Employeur"])
    email = st.sidebar.text_input("Votre Email")
    if st.sidebar.checkbox("J'accepte les CGV"):
        if st.sidebar.button("Envoyer Magik Link"): st.sidebar.success("Lien envoyé !")
    st.stop()

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Accueil", "Espace de Travail", "CGV"])

# --- LOGIQUE ---
if menu == "Accueil":
    st.markdown(TEXTES["presentation"])

elif menu == "Espace de Travail":
    # ESPACE CANDIDAT
    if st.session_state.role == "Candidat":
        st.header("Espace Candidat")
        t1, t2 = st.tabs(["Candidature (Scrapping)", "Entretiens"])
        with t1:
            secteur = st.text_input("Secteur visé")
            if st.button("Identifier cibles"):
                st.session_state.cibles = moteur_ia(f"Donne 3 entreprises secteur {secteur}. Format: Nom|Email.")
            st.write(st.session_state.get("cibles", ""))
        with t2:
            st.warning(f"Lien Visio : [Rejoindre Jitsi]({creer_salle_jitsi('candidat')})")

    # ESPACE EMPLOYEUR
    elif st.session_state.role == "Employeur":
        st.header("Espace Employeur")
        t1, t2 = st.tabs(["Talents & Dispatch", "Gestion Visio"])
        with t1:
            pays = st.selectbox("Pays", ["France", "Madagascar", "Canada"])
            if st.button("Rechercher candidats"):
                st.session_state.candidats = moteur_ia(f"Suggère 3 profils en {pays}.")
            st.write(st.session_state.get("candidats", ""))
            if st.button("👍 Déverrouiller et Dispatcher"):
                st.success("Candidat dispatché et notifié par email !")
        with t2:
            st.info("Programmez vos entretiens et lancez la visio :")
            st.link_button("Lancer salle de recrutement Jitsi", creer_salle_jitsi("recruteur"))

elif menu == "CGV":
    st.markdown(TEXTES["cgv"])
