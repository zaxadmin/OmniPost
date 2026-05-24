import streamlit as st
import pandas as pd
import os
import json
import urllib.parse
from datetime import date
from groq import Groq

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "user_type": None, "premium": False, "scraping_count": 0, "anonymat_leve": False})

# --- FONCTIONS IA ---
def extraire_20_contacts(metier):
    prompt = f"Génère une liste JSON de 20 entreprises réelles avec email pour {metier}. Format: {{\"entreprises\": [{{\"nom\": \"...\", \"email\": \"...\"}}, ...]}}"
    response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-70b-8192", response_format={"type": "json_object"})
    return response.choices[0].message.content

# --- INTERFACE ---
if not st.session_state.auth:
    st.title("zipngo 👍")
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"): st.session_state.update({"auth": True, "user_type": role}); st.rerun()
else:
    with st.sidebar:
        st.write(f"Utilisateur : **{st.session_state.user_type}** 👍")
        menu = st.radio("Navigation", ["Tableau de bord", "Candidature Spontanée", "Recherche Talents", "Gestion Entretiens", "📂 ATS - Mon Suivi", "Mon Compte"])
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()
        
        with st.expander("📖 Mode d'emploi"):
            if st.session_state.user_type == "Candidat":
                st.write("1. Scrapez 20 cibles. 👍\n2. Envoyez via mail perso.\n3. Confirmez pour l'ATS. 👍\n4. Proposez/Acceptez entretien sécurisé.")
            else:
                st.write("1. Hub de diffusion. 👍\n2. Sélectionnez vos talents.\n3. Gérez la levée d'anonymat. 👍")

    if menu == "Candidature Spontanée" and st.session_state.user_type == "Candidat":
        st.header("Sourcing IA (Batch 20)")
        metier = st.text_input("Métier visé")
        if st.button("🔍 Générer 20 entreprises"):
            if st.session_state.scraping_count < 20 or st.session_state.premium:
                res = json.loads(extraire_20_contacts(metier))
                st.session_state.liste_candidatures = res['entreprises']
                st.session_state.scraping_count += 1
            else: st.error("Limite atteinte.")
            
        if "liste_candidatures" in st.session_state:
            for item in st.session_state.liste_candidatures:
                st.write(f"--- **{item['nom']}** ---")
                st.warning("⚠️ Vérifiez votre CV.")
                st.markdown(f'<a href="mailto:{item["email"]}">✉️ Préparer envoi</a>', unsafe_allow_html=True)
                if st.button(f"Confirmer envoi 👍", key=item['nom']):
                    pd.DataFrame([{"Entreprise": item['nom'], "Email": item['email'], "Date": str(date.today())}]).to_csv('tiroir_candidat.csv', mode='a', header=not os.path.exists('tiroir_candidat.csv'), index=False)
                    st.success("Enregistré 👍")

    elif menu == "Gestion Entretiens":
        st.header("🤝 Espace Entretiens Sécurisé")
        if not st.session_state.anonymat_leve:
            if st.session_state.user_type == "Employeur":
                if st.button("Proposer entretien 👍"): st.success("Proposition envoyée.")
            else:
                if st.button("Accepter le créneau 👍"): st.success("Créneau validé.")
            
            if st.button("🤝 Lever l'anonymat (Double clic requis)"):
                st.session_state.anonymat_leve = True
                st.rerun()
        else:
            st.success("Confidentialité levée. 👍")
            st.download_button("📥 Télécharger CV & Récap", data="CV_Data...", file_name="candidature.txt")
            st.link_button("🎥 Salle Jitsi", f"https://meet.jit.si/zipngo-{st.session_state.user_type}")
            if st.button("🔄 Retour à l'anonymat"):
                st.session_state.anonymat_leve = False
                st.rerun()

    elif menu == "Mon Compte":
        st.header("Paramètres")
        if not st.session_state.premium and st.button("💎 Activer Premium"): st.session_state.premium = True
        st.markdown("--- © 2026 zipngo | Liliane RAKOTOBE")
