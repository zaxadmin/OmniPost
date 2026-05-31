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
st.markdown("""
<div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #4169E1; margin-bottom: 20px;'>
    <h3 style='margin-top: 0;'>🚀 Boostez votre carrière avec zipngo</h3>
    <p>La solution tout-en-un pour <b>optimiser vos CVs</b>, <b>cibler les meilleures entreprises</b> et <b>réussir vos entretiens</b> grâce à l'intelligence artificielle.</p>
</div>
""", unsafe_allow_html=True)

if not cgv:
    st.warning("Veuillez accepter les CGV dans la barre latérale pour commencer.")
    st.stop()

# --- LOGIQUE D'ONBOARDING ET SÉPARATION DES RÔLES ---
user = supabase.auth.get_user()
profil = None
if user:
    profil = supabase.table("profils").select("*").eq("email", user.user.email).execute().data

if not profil:
    st.subheader("Bienvenue ! Configurez votre profil pour continuer :")
    choix = st.radio("Vous êtes :", ["Candidat", "Recruteur"])
    if choix == "Candidat":
        cv_up = st.file_uploader("Uploadez votre CV", type=["pdf"])
        email_c = st.text_input("Email de contact")
        if st.button("Valider mon profil Candidat"):
            supabase.table("profils").insert({"email": user.user.email, "role": "candidat", "details": {"email": email_c}}).execute()
            st.rerun()
    else:
        nom = st.text_input("Nom de l'entreprise")
        siret = st.text_input("SIRET / SIREN")
        tel = st.text_input("Téléphone")
        email_r = st.text_input("Email de réception des candidatures")
        if st.button("Valider mon profil Recruteur"):
            supabase.table("profils").insert({"email": user.user.email, "role": "recruteur", "details": {"nom": nom, "siret": siret, "tel": tel, "email_recep": email_r}}).execute()
            st.rerun()
    st.stop()
# --- AJOUTEZ CE BLOC JUSTE APRÈS VOTRE LOGIQUE D'ONBOARDING ---

# Si vous êtes l'admin, on affiche les deux espaces pour tester
if user.user.email == "creationsites06@gmail.com":
    st.info("🛠️ Mode Administrateur activé : accès total aux deux espaces.")
    tab_test_c, tab_test_r = st.tabs(["🚀 Espace Candidat (Admin)", "💼 Espace Recruteur (Admin)"])
    
    with tab_test_c:
        # [Insérer ici tout le bloc de code de l'interface Candidat]
        st.write("Interface Candidat complète...")
        
    with tab_test_r:
        # [Insérer ici tout le bloc de code de l'interface Recruteur]
        st.write("Interface Recruteur complète...")
    
    st.stop() # Empêche l'affichage du reste du code pour éviter les doublons

# --- ESPACE UTILISATEUR ---
role = profil[0]['role']

if role == "candidat":
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[1]:
        st.subheader("📄 Mes documents")
        col_up, col_down = st.columns(2)
        with col_up:
            st.write("📤 **CV Originaux uploadés**")
            st.file_uploader("Ajouter un nouveau CV", type=["pdf"])
        with col_down:
            st.write("⬇️ **CV Relookés téléchargeables**")
            st.download_button("Télécharger CV Optimisé", data=b"data", file_name="Mon_CV_Optimise.pdf")
    with dossiers[3]:
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
    with dossiers[4]:
        st.subheader("🎤 Entraînement et Historique")
        sub_t1, sub_t2 = st.tabs(["🤖 Entraînement IA", "📅 Historique"])
        with sub_t1:
            poste = st.text_input("Poste visé")
            if st.button("Poser une question"):
                q = client.chat.completions.create(messages=[{"role": "user", "content": f"Pose une question d'entretien pour {poste}"}], model="llama-3.3-70b-versatile").choices[0].message.content
                st.info(f"Recruteur : {q}")
        with sub_t2:
            st.write("Retrouvez ici vos prochains rendez-vous et vos retours d'entretiens passés.")

elif role == "recruteur":
    st.subheader("💼 Espace Recruteur")
    st.info("📢 **Gestion des recrutements** : Gérez vos offres et triez vos candidats.")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-family: sans-serif;'>
    <p>Créé par <b>Liliane RAKOTOBE</b> | Propulsé par <b>zaxx.app</b></p>
    <p>Contact <a href='mailto:creationsites06@gmail.com'>📧 </a></p>
</div>
""", unsafe_allow_html=True)
