import streamlit as st
import datetime
import pandas as pd
import io
import json
import urllib.parse
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- SIDEBAR ---
st.sidebar.title("🔐 Accès & Paramètres")
email_auth = st.sidebar.text_input("📧 Votre email pour Magic Link")
if st.sidebar.button("Envoyer lien de connexion"):
    try:
        supabase.auth.sign_in_with_otp({"email": email_auth})
        st.sidebar.success("Vérifiez vos emails !")
    except Exception: st.sidebar.error("Erreur d'envoi")

langues = ["Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", "Português", "Nederlands", "中文", "日本語", "한국어", "العربية", "हिन्दी", "Русский", "Türkçe", "Polski", "Svenska", "Dansk", "Suomi", "Norsk"]
st.session_state.langue = st.sidebar.selectbox("🌐 Sélectionner une langue", langues)

st.sidebar.markdown("---")
st.sidebar.warning("🚀 **Passez au Premium** pour un accès illimité aux outils de sourcing et à l'IA.")
if st.sidebar.button("💳 Souscrire au Premium (39€/mois)"):
    st.sidebar.info("Redirection...")

cgv = st.sidebar.checkbox("J'accepte les CGV")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("### Votre ATS intelligent pour booster vos candidatures et recrutements.")

if not cgv:
    st.warning("Veuillez accepter les CGV dans la barre latérale pour commencer.")
    st.stop()

tab_candidat, tab_employeur = st.tabs(["🚀 Espace Candidat", "💼 Espace Recruteur"])

with tab_candidat:
    st.info("💡 **Mode d'emploi** : Gérez vos CVs, sourcez des opportunités et préparez vos entretiens.")
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    
    with dossiers[1]: # GESTION DES CVS
        st.subheader("📄 Mes documents")
        col_up, col_down = st.columns(2)
        with col_up:
            st.write("📤 **CV Originaux uploadés**")
            # Logique de récupération des fichiers depuis Supabase Storage
            st.file_uploader("Ajouter un nouveau CV", type=["pdf"])
        with col_down:
            st.write("⬇️ **CV Relookés téléchargeables**")
            # Exemple de bouton de téléchargement pour fichier relooké
            st.download_button("Télécharger CV Optimisé", data=b"data", file_name="Mon_CV_Optimise.pdf")

    with dossiers[3]: # SOURCING
        st.subheader("🌐 Sourcing (Recherche & Messagerie)")
        cat = st.selectbox("Domaine", ["Restauration", "Informatique", "BTP", "Commerce"])
        ville = st.text_input("Ville cible")
        if st.button("🔍 Rechercher 20 contacts"):
            prompt = f"Donne 20 emails pros pour '{cat}' à '{ville}'. Format : liste d'emails séparés par virgules."
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.session_state.emails = [e.strip() for e in res.split(',')]
            st.rerun()
        if 'emails' in st.session_state:
            st.table(pd.DataFrame(st.session_state.emails, columns=["Emails identifiés"]))
            dest, bcc = st.session_state.emails[0], ",".join(st.session_state.emails[1:20])
            mailto_link = f"mailto:{dest}?bcc={bcc}&subject=Candidature&body=Madame, Monsieur, Veuillez trouver mon CV ci-joint."
            st.markdown(f"<a href='{mailto_link}' style='padding: 10px; background: #4169E1; color: white; border-radius: 5px; text-decoration: none;'>📧 Ouvrir Messagerie</a>", unsafe_allow_html=True)

    with dossiers[4]: # ENTRETIEN
        st.subheader("🎤 Entraînement et Historique")
        sub_t1, sub_t2 = st.tabs(["🤖 Entraînement IA", "📅 Historique"])
        with sub_t1:
            poste = st.text_input("Poste visé")
            if st.button("Poser une question"):
                q = client.chat.completions.create(messages=[{"role": "user", "content": f"Pose une question d'entretien pour {poste}"}], model="llama-3.3-70b-versatile").choices[0].message.content
                st.info(f"Recruteur : {q}")
        with sub_t2:
            st.write("Retrouvez ici vos prochains rendez-vous et vos retours d'entretiens passés.")

with tab_employeur:
    st.subheader("📢 Création et Dispatch automatique")
    # Logique Recruteur conservée...

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-family: sans-serif;'>
    <p>Créé par <b>Liliane RAKOTOBE</b> | Propulsé par <b>zaxx.app</b></p>
    <p>Besoin d'assistance ? <a href='mailto:creationsites06@gmail.com'>📧 creationsites06@gmail.com</a></p>
</div>
""", unsafe_allow_html=True)
