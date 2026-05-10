import streamlit as st
import google.generativeai as genai
import json

def get_model():
    """Initialise le modèle Gemini 1.5 Flash."""
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

def coach_ia(cv_text, action, context="", lang="Français"):
    """Optimisation de CV, rédaction de lettres et passage d'ATS."""
    model = get_model()
    prompts = {
        "relook": f"Agis en expert branding. Embellis ce CV en {lang} (impact et résultats) : {cv_text}",
        "adapt": f"Agis en expert ATS. Optimise ce CV en {lang} pour le poste {context} (mots-clés stratégiques) : {cv_text}",
        "lettre": f"Rédige une lettre de motivation percutante en {lang} pour {context} basée sur : {cv_text}"
    }
    return model.generate_content(prompts[action]).text

def analyze_matching(cv_text, job_desc):
    """Calcule le score ATS entre le CV et l'offre d'emploi."""
    model = get_model()
    prompt = f"""
    Analyse le matching CV/Offre. Réponds uniquement en JSON: {{"score": 0, "verdict": ""}}. 
    Offre: {job_desc} 
    CV: {cv_text}
    """
    try:
        res = model.generate_content(prompt)
        clean = res.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)
    except: 
        return {"score": 0, "verdict": "Erreur d'analyse IA."}

def generate_offer(job_title, lang="Français"):
    """Génère une offre d'emploi pour le recruteur."""
    model = get_model()
    return model.generate_content(f"Rédige une offre d'emploi pro en {lang} pour : {job_title}").text
