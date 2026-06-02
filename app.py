import streamlit as st
import datetime
import pandas as pd
import io
import re
import json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import resend
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]


# --- FONCTION TRADUCTION IA ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content


# --- FONCTIONS D'ORIGINE ---
def creer_pdf_cv_pro(texte_ia, nom_fichier, style):
    pdf = FPDF()
    pdf.add_page()
    if style == "Classique": pdf.set_font("Times", 'B', 16)
    elif style == "Moderne": pdf.set_font("Arial", 'B', 18)
    else: pdf.set_font("Courier", 'B', 16)
    pdf.cell(200, 10, txt="Mon CV Optimisé", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=texte_ia)
    pdf.output(nom_fichier)

def afficher_cgv():
    texte_cgv = "1. Accès Candidat 6€/3mois | Recruteur 39€/mois. 2. Limites Gratuit : 1 CV/mois, 1 campagne/mois. 3. Premium : 3 CVs/semaine, 20 mails/jour."
    st.markdown(traduire_avec_ia(texte_cgv, st.session_state.langue))

def archiver_entretien(candidat_id, statut, lien_jitsi, feedback=""):
    supabase.table("archives_entretiens").insert({
        "candidat_id": candidat_id,
        "statut": statut,
        "lien_jitsi": lien_jitsi,
        "feedback": feedback,
        "date_archivage": str(datetime.datetime.now())
    }).execute()


# --- NOUVELLES FONCTIONS ---
def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse pour le poste '{metier}'. Retourne uniquement un JSON structuré avec: 'header' (nom, titre_poste, contact), 'sidebar' (contenu), 'main' (titre, corps), 'mots_cles_ajoutes'. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("
```", ""))

def appliquer_design_geometrique(pdf, data):
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, data['header']['nom'], ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, data['header']['contact'])
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, data['sidebar']['contenu'])
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, data['header']['titre_poste'], ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, data['main']['titre'], ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, data['main']['corps'])


# --- FONCTIONS RÉELLES DE DIFFUSION & MATCHING ---
def diffuser_france_travail(config, metier, ville, description, contrat):
    auth_url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
    payload = {
        "grant_type": "client_credentials",
        "client_id": config.get("france_travail_client_id"),
        "client_secret": config.get("france_travail_client_secret"),
        "scope": "api_offresdepotv1"
    }
    try:
        token_res = requests.post(auth_url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload)
        token = token_res.json().get("access_token")
        
        api_url = "https://api.francetravail.io/partenaire/offresdepot/v1/offres"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        offre_payload = {
            "intitule": metier,
            "lieuTravail": {"libelle": ville},
            "description": description,
            "typeContrat": contrat
        }
        res = requests.post(api_url, headers=headers, json=offre_payload)
        return res.status_code == 201
    except:
        return False

def diffuser_facebook(config, texte_offre):
    page_id = config.get("facebook_page_id")
    token = config.get("facebook_token")
    url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    payload = {"message": f"📢 NOUVELLE OFFRE D'EMPLOI\n\n{texte_offre}", "access_token": token}
    try:
        res = requests.post(url, data=payload)
        return res.status_code == 200
    except:
        return False

def diffuser_remote_ok(config, metier, description, salaire):
    url = "https://remoteok.com/api/post"
    payload = {
        "api_key": config.get("remote_ok_api_key"),
        "title": metier,
        "description": description,
        "salary_min": int(salaire * 150)
    }
    try:
        res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        return res.status_code == 200
    except:
        return False

def marquer_pour_flux(id_offre, plateformes_flux):
    try:
        supabase.table("mes_offres").update({"flux_cibles": plateformes_flux}).eq("id", id_offre).execute()
        return True
    except:
        return False

def executer_matching_ia(id_offre, texte_offre):
    candidats_db = supabase.table("cvs").select("id, nom_fichier, contenu").execute()
    if not candidats_db.data:
        return
    for candidat in candidats_db.data:
        prompt = f"""
        Tu es un expert en recrutement (ATS). Evalue la pertinence du CV suivant pour l'offre d'emploi fournie.
        OFFRE D'EMPLOI :
        {texte_offre}
        CV DU CANDIDAT :
        {candidat['contenu']}
        Renvoie UNIQUEMENT un objet JSON (sans bloc de code 
