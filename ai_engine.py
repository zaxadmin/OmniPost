import streamlit as st
import google.generativeai as genai

def get_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    return genai.GenerativeModel('gemini-1.5-flash')

def coach_ia(cv_text, action, context="", lang="Français"):
    model = get_model()
    prompt = f"Réponds en {lang}. CV: {cv_text}. Action: {action} avec contexte: {context}"
    return model.generate_content(prompt).text

def generate_offer(job_title, lang="Français"):
    model = get_model()
    return model.generate_content(f"Rédige une offre d'emploi en {lang} pour : {job_title}").text
