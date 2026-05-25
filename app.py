import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq
from supabase import create_client
import streamlit.components.v1 as components
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | .zaxx.app", layout="wide")
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- INITIALISATION SESSION ---
if "auth" not in st.session_state:
    st.session_state.update({
        "auth": False, "cgv_validee": False, "bienvenue_vue": False, 
        "profil_complet": False, "user_type": None, "user_email": None,
        "entretiens": []
    })

# --- FONCTIONS IA & LOGIQUE ---
def generer_ia(prompt):
    response = client_groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192"
    )
    return response.choices[0].message.content

def afficher_visio_jitsi(nom_salle):
    components.iframe(f"https://meet.jit.si/{nom_salle}", height=600)

# --- FLUX AUTHENTIFICATION ---
if not st.session_state.auth:
    st.markdown('<h1 style="color:#000080;">zip<span style="color:#1E90FF;">ngo</span> 👍</h1>', unsafe_allow_html=True)
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    email = st.text_input("Votre email :")
    if st.button("✨ Recevoir mon lien magique"):
        st.session_state.update({"auth": True, "user_email": email, "user_type": role})
        st.rerun()

elif not st.session_state.cgv_validee:
    st.write("## 📜 CGVU")
    if st.checkbox("J'accepte"):
        if st.button("Confirmer"):
            st.session_state.cgv_validee = True
            st.rerun()

elif not st.session_state.bienvenue_vue:
    st.balloons()
    st.write("# Bienvenue chez zipngo 👋")
    if st.button("Continuer"):
        st.session_state.bienvenue_vue = True
        st.rerun()

# --- DASHBOARD & TOOLS ---
else:
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Menu", ["Dashboard", "Tiroir Entretien", "Prospection B2B"])
    
    if menu == "Dashboard":
        if st.session_state.user_type == "Employeur":
            st.header("📊 Candidatures")
            # Simulation de tri
            candidats = [{"nom": "Jean"}, {"nom": "Marie"}]
            for c in candidats:
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"Candidat : {c['nom']}")
                if col2.button("👍", key=f"up_{c['nom']}"):
                    st.session_state.entretiens.append(c)
                col3.button("👎", key=f"down_{c['nom']}")
        else:
            st.header("🚀 Espace Candidat")
            cv = st.text_area("Optimisation CV :")
            if st.button("Analyser"): st.write(generer_ia(f"Optimise : {cv}"))

    elif menu == "Tiroir Entretien":
        st.header("📹 Entretien Vidéo")
        for ent in st.session_state.entretiens:
            if st.button(f"Lancer visio avec {ent['nom']}"):
                afficher_visio_jitsi(f"zipngo-{ent['nom']}")

    elif menu == "Prospection B2B":
        st.header("🔍 Agent IA")
        secteur = st.selectbox("Secteur :", ["Tech", "Finance", "Santé"])
        if st.button("Rechercher"):
            st.write(generer_ia(f"Liste 20 entreprises en {secteur} avec contacts."))

    if st.sidebar.button("Déconnexion"): st.session_state.clear(); st.rerun()
