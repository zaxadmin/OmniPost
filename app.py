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

# --- LISTE DES 20 LANGUES ---
LANGUES = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", 
           "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", 
           "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", 
           "Bahasa Indonesia", "ภาษาไทย (Thaï)"]

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

# --- MOTEUR DE MATCHING AUTOMATIQUE ---
def executer_matching_ia_depuis_offre(id_offre, texte_offre, offre_remote, offre_pays):
    try:
        candidats_db = supabase.table("cvs").select("*").execute().data
        if not candidats_db: return
        for candidat in candidats_db:
            if not (offre_remote and candidat.get("is_remote", False)):
                if candidat.get("pays", "France") != offre_pays: continue
            try:
                prompt = f"Calcule le score de matching (0 à 100) en JSON entre cette offre : {texte_offre} et ce CV : {candidat['contenu']}"
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                resultat_json = extraire_json_propre(res.choices[0].message.content)
                supabase.table("matching_offres_candidats").insert({"offre_id": id_offre, "candidat_id": candidat["id"], "score": int(resultat_json.get("score", 0)), "justification": resultat_json["justification"], "source": candidat.get("source", "app")}).execute()
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
                supabase.table("matching_offres_candidats").insert({"offre_id": offre["id"], "candidat_id": id_cv, "score": int(resultat_json.get("score", 0)), "justification": resultat_json["justification"], "source": source}).execute()
            except: pass
    except: pass

def simuler_ia_reception_email(email_recu, nom_candidat, email_reel, tel_reel, texte_cv):
    res_cv = supabase.table("cvs").insert({"nom_fichier": nom_candidat, "contenu": texte_cv, "pays": "France", "ville": "Externe", "is_remote": False, "source": "email", "email_reel": email_reel, "tel_reel": tel_reel, "anonymat_leve": True}).execute()
    if res_cv.data:
        executer_matching_automatique_cv(res_cv.data[0]["id"], texte_cv, False, "France", "Externe", source="email")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

if 'langue' not in st.session_state: st.session_state.langue = "Français"
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue", LANGUES, index=0)

tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil & Mode d'emploi", "🚀 Candidat", "💼 Employeur"]])

# --- ZONE CANDIDAT ---
with tab_candidat:
    st.button("💎 Passer en Premium", key="btn_cand_premium", type="primary")
    st.markdown(f"### 🚀 {traduire_avec_ia('Espace Candidat Anonymisé', st.session_state.langue)}")
    # ... (Ajoutez ici tout le reste de votre logique candidat originale)

# --- ZONE EMPLOYEUR ---
with tab_employeur:
    st.button("💎 Passer en Premium", key="btn_emp_premium", type="primary")
    st.header("💼 Espace Recruteur")
    # ... (Ajoutez ici tout le reste de votre logique employeur originale)

# --- ACCUEIL & CGV ---
with tab_home:
    with st.expander("⚖️ Conditions Générales de Vente (CGV)"):
        st.markdown("""
        ### Tarification :
        - **Accès Candidat :** 6€ pour 3 mois.
        - **Accès Employeur :** 39€ par mois.
        ### Non-Remboursement :
        Service numérique à exécution immédiate : aucun remboursement possible après activation.
        ### Suppression de compte :
        Droit à l'effacement total de vos données sur simple demande par email. Traitement sous 48h.
        """)

# --- PIED DE PAGE ---
st.markdown("---")
st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b> <a href='mailto:creationsites06@gmail.com'>✉️</a></div>", unsafe_allow_html=True)
