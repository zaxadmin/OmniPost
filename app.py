import streamlit as st
import datetime
import pandas as pd
import io
import re
import json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
import resend
import requests
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium Global", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]


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


# --- MOTEUR DE MATCHING ARRIÈRE-PLAN IA (> 50%) ---
def executer_matching_automatique_cv(id_cv, contenu_cv, candidat_remote, candidat_pays, candidat_ville):
    """S'exécute immédiatement après l'upload d'un CV pour chercher les offres correspondantes"""
    try:
        offres_db = supabase.table("mes_offres").select("*").execute().data
        if not offres_db:
            return
            
        for offre in offres_db:
            offre_remote = offre.get("is_remote", False)
            offre_pays = offre.get("pays", "France")
            
            # Gestion de la barrière pays/ville grâce au mode Remote
            if not (candidat_remote and offre_remote):
                if candidat_pays != offre_pays:
                    continue  # Saute cette offre si les pays ne correspondent pas

            prompt = f"""
            Evalue la pertinence du CV suivant pour l'offre d'emploi fournie.
            OFFRE D'EMPLOI :
            {offre['contents']}
            CV DU CANDIDAT :
            {contenu_cv}
            Renvoie UNIQUEMENT un objet JSON (sans bloc de code ```json) structuré ainsi :
            {{
                "score": <un entier entre 0 et 100>,
                "justification": "<2 phrases maximum expliquant le score>"
            }}
            """
            try:
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.1)
                brut = res.choices[0].message.content.strip()
                
                # --- CORRECTION SÉCURISÉE DE LA LIGNE 74 ---
                clean_matching = brut.replace("```json", "").replace("```", "")
                resultat_json = json.loads(clean_matching)
                
                if int(resultat_json["score"]) >= 50:
                    supabase.table("matching_offres_candidats").insert({
                        "offre_id": offre["id"],
                        "candidat_id": id_cv,
                        "score": resultat_json["score"],
                        "justification": resultat_json["justification"]
                    }).execute()
            except:
                pass
    except:
        pass


def executer_matching_ia_depuis_offre(id_offre, texte_offre, offre_remote, offre_pays):
    """S'exécute lorsqu'un employeur crée une nouvelle offre"""
    try:
        candidats_db = supabase.table("cvs").select("*").execute().data
        if not candidats_db: return
        for candidat in candidats_db:
            cand_remote = candidat.get("is_remote", False)
            cand_pays = candidat.get("pays", "France")
            
            if not (offre_remote and cand_remote):
                if offre_pays != cand_pays: continue
