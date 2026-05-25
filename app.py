import streamlit as st
import requests
from groq import Groq
from supabase import create_client

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")

# Initialisation des clients (Secrets gérés dans Streamlit Cloud)
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTION D'ENVOI EMAIL (RESEND) ---
def envoyer_email_dispatch(dest, sujet, contenu):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {st.secrets['RESEND_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "onboarding@resend.dev",
        "to": dest,
        "subject": sujet,
        "html": f"<p>{contenu}</p>"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 200

# --- FONCTION IA ---
def moteur_ia(prompt):
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], 
            model="llama-3.3-70b-versatile"
        )
        return res.choices[0].message.content
    except Exception as e: 
        return f"Erreur IA : {e}"

# --- CSS & DESIGN ---
st.markdown("""
    <style>
    .zip { color: #000080; font-weight: bold; font-size: 2.5rem; }
    .ngo { color: #4169E1; font-weight: bold; font-size: 2.5rem; }
    </style>
    <div><span class="zip">zip</span><span class="ngo">ngo</span>.zaxx.app</div>
""", unsafe_allow_html=True)

# --- NAVIGATION (ONGLETS DIRECTS) ---
tab_candidat, tab_employeur, tab_cgv = st.tabs(["🚀 Espace Candidat", "💼 Espace Employeur", "📜 CGV"])

with tab_candidat:
    st.header("Interface Candidat")
    secteur = st.text_input("Secteur visé pour le scraping")
    if st.button("Lancer Scrapping 20 cibles"):
        with st.spinner("Recherche IA en cours..."):
            st.write(moteur_ia(f"Donne 20 entreprises en {secteur} avec emails."))
    
    cv = st.text_area("Copiez votre CV ici")
    if st.button("Optimiser mon CV avec IA"):
        with st.spinner("Amélioration en cours..."):
            st.write(moteur_ia(f"Améliore ce CV pour le rendre plus percutant : {cv}"))

with tab_employeur:
    st.header("Interface Employeur (ATS)")
    pays = st.selectbox("Pays ciblé", ["France", "Madagascar", "Canada", "Remote"])
    
    if st.button("Rechercher Talents"):
        with st.spinner("Analyse des profils..."):
            st.write(moteur_ia(f"Suggère 5 profils candidats qualifiés en {pays}."))
    
    st.markdown("---")
    email_candidat = st.text_input("Email du candidat à déverrouiller")
    
    if st.button("👍 Déverrouiller et Dispatcher"):
        if email_candidat:
            # 1. Mise à jour dans Supabase
            try:
                supabase.table("candidats").update({"est_debloque": True}).eq("email", email_candidat).execute()
                
                # 2. Notification Mail via Resend
                sujet = "Zipngo : Félicitations, vous avez été sélectionné !"
                contenu = "Bonjour, un recruteur a déverrouillé votre profil sur Zipngo. Voici le lien pour votre entretien : https://meet.jit.si/zipngo-entretien-privé"
                
                if envoyer_email_dispatch(email_candidat, sujet, contenu):
                    st.success(f"Candidat {email_candidat} déverrouillé et notifié par email !")
                else:
                    st.error("Erreur lors de l'envoi de l'email via Resend.")
            except Exception as e:
                st.error(f"Erreur base de données : {e}")
        else:
            st.warning("Veuillez entrer l'email du candidat.")

with tab_cgv:
    st.markdown("""
    ### Conditions Générales de Vente
    Mise à jour : 25 mai 2026.
    Zipngo est un service premium de recrutement par IA.
    Accès illimité aux profils via abonnement.
    """)
