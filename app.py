import streamlit as st
import pandas as pd
import io
import json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | Connexion Professionnelle", layout="wide")
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
cgv = st.sidebar.checkbox("J'accepte les CGV")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

st.markdown("""
<div style='background-color: #f0f2f6; padding: 25px; border-radius: 15px; border-left: 6px solid #4169E1; margin-bottom: 20px;'>
    <h2 style='color: #000080; margin-top: 0;'>zipngo : Simplifiez vos rencontres professionnelles</h2>
    <p style='font-size: 1.1em;'>Trouver le bon talent ou le poste idéal ne devrait pas être un parcours du combattant.</p>
    <p><b>zipngo</b> est l'espace qui connecte vos ambitions en rendant chaque étape simple, fluide et rapide. Gagnez en sérénité et concentrez-vous sur l'essentiel : <b>la rencontre.</b></p>
</div>
""", unsafe_allow_html=True)

if not cgv:
    st.warning("Veuillez accepter les CGV dans la barre latérale pour commencer.")
    st.stop()

# --- FONCTIONS DES ESPACES ---
def render_candidat():
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[1]:
        st.subheader("📄 Mes documents")
        col_up, col_down = st.columns(2)
        col_up.file_uploader("Ajouter un nouveau CV", type=["pdf"])
        col_down.download_button("Télécharger CV Optimisé", data=b"data", file_name="Mon_CV_Optimise.pdf")
    with dossiers[3]:
        st.subheader("🌐 Sourcing (Recherche & Messagerie)")
        cat = st.selectbox("Domaine", ["Restauration", "Informatique", "BTP", "Commerce"])
        ville = st.text_input("Ville cible")
        if st.button("🔍 Rechercher 20 contacts"): st.rerun()
    with dossiers[4]:
        st.subheader("🎤 Entraînement et Historique")
        st.tabs(["🤖 Entraînement", "📅 Historique"])

def render_recruteur():
    st.subheader("💼 Espace Recruteur")
    st.info("📢 **Gestion des recrutements** : Gérez vos offres et triez vos candidats.")

# --- LOGIQUE D'ONBOARDING ET ACCÈS ---
user = supabase.auth.get_user()
profil = supabase.table("profils").select("*").eq("email", user.user.email).execute().data if user else None

if not profil and user:
    st.subheader("Bienvenue ! Configurez votre profil :")
    choix = st.radio("Vous êtes :", ["Candidat", "Recruteur"])
    if st.button("Valider"):
        role = choix.lower()
        supabase.table("profils").insert({"email": user.user.email, "role": role}).execute()
        st.rerun()
    st.stop()

# --- AFFICHAGE FINAL ---
if user and user.user.email == "creationsites06@gmail.com":
    st.info("🛠️ Mode Administrateur activé")
    t1, t2 = st.tabs(["🚀 Espace Candidat", "💼 Espace Recruteur"])
    with t1: render_candidat()
    with t2: render_recruteur()
elif profil:
    role = profil[0]['role']
    if role == "candidat": render_candidat()
    else: render_recruteur()

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-family: sans-serif;'>
    <p>Créé par <b>Liliane RAKOTOBE</b> | Propulsé par <b>zaxx.app</b></p>
    <p>Contact
        <a href='mailto:creationsites06@gmail.com' style='text-decoration: none;'>
            📧
        </a>
    </p>
</div>
""", unsafe_allow_html=True)
