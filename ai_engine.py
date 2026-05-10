import streamlit as st
import google.generativeai as genai
import json

def get_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

def coach_ia(cv_text, action, context="", lang="Français"):
    model = get_model()
    if action == "relook":
        prompt = f"Agis en expert branding. Embellis ce CV en {lang} (mots d'action, impact) : {cv_text}"
    elif action == "adapt":
        prompt = f"Agis en expert ATS. Optimise ce CV en {lang} pour passer les filtres sur ce poste : {context}. CV original : {cv_text}"
    else:
        prompt = f"Rédige une lettre de motivation percutante en {lang} pour : {context}. Basée sur : {cv_text}"
    
    return model.generate_content(prompt).text

def analyze_matching(cv_text, job_desc):
    model = get_model()
    prompt = f"Compare ce CV : {cv_text} et cette Offre : {job_desc}. Réponds EXCLUSIVEMENT en JSON : {{\"score\": 0, \"verdict\": \"\"}}"
    try:
        res = model.generate_content(prompt)
        clean_json = res.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except: return {"score": 0, "verdict": "Erreur d'analyse."}

def generate_offer(job_title, lang="Français"):
    model = get_model()
    return model.generate_content(f"Rédige une offre d'emploi pro en {lang} pour : {job_title}").text
