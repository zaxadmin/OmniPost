import streamlit as st
import smtplib
from email.message import EmailMessage
from groq import Groq
from supabase import create_client

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTIONS IA ---
def moteur_ia(prompt):
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return res.choices[0].message.content
    except Exception as e: return f"Erreur IA : {e}"

# --- LOGIQUE D'EMAIL RÉEL ---
def envoyer_email_dispatch(dest, sujet, contenu):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(st.secrets["GMAIL_USER"], st.secrets["GMAIL_PASS"])
        msg = EmailMessage()
        msg.set_content(contenu)
        msg['Subject'] = sujet
        msg['From'] = "contact@zaxx.app"
        msg['To'] = dest
        smtp.send_message(msg)

# --- CSS & LOGO ---
st.markdown("""
    <style>
    .zip { color: #000080; font-weight: bold; font-size: 2.5rem; }
    .ngo { color: #4169E1; font-weight: bold; font-size: 2.5rem; }
    .zaxx { font-size: 1rem; color: #555; display: block; margin-bottom: 20px; }
    </style>
    <div><span class="zip">zip</span><span class="ngo">ngo</span><span class="zaxx">.zaxx.app</span></div>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["Accueil", "Espace de Travail", "CGV"])

# --- ESPACE CANDIDAT ---
if st.session_state.get("role") == "Candidat":
    st.header("Espace Candidat")
    tab1, tab2 = st.tabs(["Scrapping & Candidatures", "Relooking CV"])
    with tab1:
        secteur = st.text_input("Secteur visé")
        if st.button("Scraper 20 cibles"):
            st.write(moteur_ia(f"Donne 20 entreprises en {secteur} avec emails. Format: Nom|Email."))
    with tab2:
        cv_text = st.text_area("Copiez votre CV ici")
        if st.button("Améliorer mon CV"):
            st.write(moteur_ia(f"Améliore ce CV pour le rendre plus percutant : {cv_text}"))

# --- ESPACE EMPLOYEUR ---
elif st.session_state.get("role") == "Employeur":
    st.header("Espace Employeur (ATS)")
    pays = st.selectbox("Pays", ["France", "Madagascar", "Canada", "Remote"])
    if st.button("Rechercher et Trier Talents"):
        st.write(moteur_ia(f"Suggère 5 profils candidats qualifiés en {pays}."))
    if st.button("👍 Déverrouiller et Dispatcher"):
        envoyer_email_dispatch("candidat@test.com", "Entretien Zipngo", "Vous êtes déverrouillé !")
        st.success("Candidat dispatché et notifié par email.")

# --- CGV ---
elif menu == "CGV":
    st.markdown("### Conditions Générales\n(Détails complets avec mise à jour du 25 mai 2026).")
