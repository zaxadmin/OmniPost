import streamlit as st
import google.generativeai as genai
import json

def get_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_job_description(job_title):
    """CÔTÉ EMPLOYEUR : Rédige l'offre automatiquement"""
    model = get_model()
    prompt = f"Rédige une offre d'emploi professionnelle pour le poste de : {job_title}. Structure avec Missions, Profil et Avantages."
    return model.generate_content(prompt).text

def analyze_cv_with_ai(cv_text, job_description):
    """CÔTÉ CANDIDAT : Calcule le score de matching"""
    model = get_model()
    prompt = f"Analyse ce CV : {cv_text} par rapport à cette OFFRE : {job_description}. Réponds uniquement en JSON: {{\"score\": 0-100, \"verdict\": \"\", \"points_forts\": []}}"
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.replace('```json', '').replace('```', ''))
    except:
        return {"score": 0, "verdict": "Erreur d'analyse"}
