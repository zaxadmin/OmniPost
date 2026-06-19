import streamlit as st
import datetime
import pandas as pd
import io
import re
import json
import os # Import indispensable pour les variables d'environnement
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
import resend
import requests
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium Global", layout="wide")

# Utilisation de os.environ.get au lieu de st.secrets
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
resend.api_key = os.environ.get("RESEND_API_KEY")

# --- CONFIGURATION DES PAYS & DEVISES ---
PAYS_CONFIG = {
    "France": {"devise": "€", "plateforme_locale": "France Travail"},
    "Madagascar": {"devise": "Ar", "plateforme_locale": "Orange MixJob / Midi"},
    "United States": {"devise": "$", "plateforme_locale": "Indeed US"},
    "Canada": {"devise": "$ CAD", "plateforme_locale": "Guichet Emploi"},
    "International / Autre": {"devise": "$", "plateforme_locale": "LinkedIn"}
}

# --- FONCTION TRADUCTION IA ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

# --- NETTOYAGE JSON SECURISE ---
def extraire_json_propre(texte_brut):
    try:
        texte_nettoye = re.sub(r"```json|```", "", texte_brut).strip()
        return json.loads(texte_nettoye)
    except:
        try:
            match = re.search(r"\{.*\}", texte_brut, re.DOTALL)
            if match: return json.loads(match.group(0))
        except: pass
    return {"score": 0, "justification": "Erreur d'analyse."}

# --- MOTEUR DE MATCHING ---
def executer_matching_ia_depuis_offre(id_offre, texte_offre, offre_remote, offre_pays):
    try:
        candidats_db = supabase.table("cvs").select("*").execute().data
        if not candidats_db: return
        for candidat in candidats_db:
            cand_remote = candidat.get("is_remote", False)
            cand_pays = candidat.get("pays", "France")
            if not (offre_remote and cand_remote):
                if cand_pays != offre_pays: continue
            try:
                prompt = f"Calcule le score de matching (0 à 100) en JSON entre cette offre : {texte_offre} et ce CV : {candidat['contenu']}"
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                resultat_json = extraire_json_propre(res.choices[0].message.content)
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": id_offre, "candidat_id": candidat["id"], "score": int(resultat_json.get("score", 0)), 
                    "justification": resultat_json["justification"], "source": candidat.get("source", "app")
                }).execute()
            except: pass
    except: pass

def executer_matching_automatique_cv(id_cv, contenu_cv, candidat_remote, candidat_pays, candidat_ville, source="app"):
    try:
        offres_db = supabase.table("mes_offres").select("*").execute().data
        if not offres_db: return
        for offre in offres_db:
            if not (candidat_remote and offre.get("is_remote", False)):
                if candidat_pays != offre.get("pays", "France"): continue
            prompt = f"Evalue le matching en JSON entre l'offre : {offre['contents']} et le CV : {contenu_cv}."
            try:
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.1)
                resultat_json = extraire_json_propre(res.choices[0].message.content)
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": offre["id"], "candidat_id": id_cv, "score": int(resultat_json.get("score", 0)), 
                    "justification": resultat_json["justification"], "source": source
                }).execute()
            except: pass
    except: pass

def simuler_ia_reception_email(email_recu, nom_candidat, email_reel, tel_reel, texte_cv):
    res_cv = supabase.table("cvs").insert({
        "nom_fichier": nom_candidat, "contenu": texte_cv, "pays": "France", "ville": "Externe",
        "is_remote": False, "source": "email", "email_reel": email_reel, "tel_reel": tel_reel, "anonymat_leve": True
    }).execute()
    if res_cv.data:
        executer_matching_automatique_cv(res_cv.data[0]["id"], texte_cv, False, "France", "Externe", source="email")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown("### 🛠️ Création & Support")
st.sidebar.markdown("**Créatrice :** Liliane RAKOTOBE")
st.sidebar.markdown('<a href="mailto:creationsites06@gmail.com" style="text-decoration: none; font-size: 20px;">✉️ <span style="font-size: 14px; vertical-align: middle;">Contact par Email</span></a>', unsafe_allow_html=True)
st.sidebar.markdown("---")

langues = ["Français", "English (US)", "Malagasy", "Español", "Deutsch"]
if 'langue' not in st.session_state: st.session_state.langue = "Français"
st.session_state.langue = st.sidebar.selectbox("🌐 Langue de l'application", langues, index=0)

tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil & Mode d'emploi", "🚀 Candidat", "💼 Employeur"]])

# --- ZONE ACCUEIL ---
with tab_home:
    st.markdown(f"## {traduire_avec_ia('Bienvenue sur zipngo, l\'ATS intelligent et anonyme sans frontières ! 🌍', st.session_state.langue)}")
    st.markdown(traduire_avec_ia("""
    **zipngo** est une plateforme de recrutement de nouvelle génération, propulsée par une Intelligence Artificielle avancée. 
    Notre mission est double : **supprimer les barrières géographiques** pour permettre le recrutement local et à l'international, et **garantir une totale équité** grâce à un système d'anonymat crypté.
    
    Sur zipngo, les processus de sélection se font uniquement sur les compétences. Les coordonnées privées (noms, téléphones, emails) restent entièrement masquées tant qu'une entente mutuelle n'a pas été scellée d'
