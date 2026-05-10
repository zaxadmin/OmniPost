import streamlit as st
import google.generativeai as genai
import json

def get_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

def coach_ia(cv_text, action, context="", lang="Français"):
    model = get_model()
    prompt = f"Réponds en {lang}. CV: {cv_text}. "
    if action == "relook": prompt += "Optimise ce CV pour le rendre pro."
    elif action == "lettre": prompt += f"Rédige une lettre de motivation pour : {context}"
    elif action == "adapt": prompt += f"Adapte ce CV au métier : {context}"
    
    return model.generate_content(prompt).text

def generate_offer(job_title, lang="Français"):
    model = get_model()
    return model.generate_content(f"Rédige une offre d'emploi en {lang} pour le poste : {job_title}").text

def analyze_matching(cv_text, job_desc):
    model = get_model()
    prompt = f"Compare ce CV : {cv_text} et cette Offre : {job_desc}. Réponds uniquement en JSON: {{\"score\": 0, \"verdict\": \"\"}}"
    try:
        res = model.generate_content(prompt)
        return json.loads(res.text.replace('```json', '').replace('```', ''))
    except: return {"score": 0, "verdict": "Erreur d'analyse"}
