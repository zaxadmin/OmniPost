import streamlit as st
import google.generativeai as genai
import json

def analyze_cv_with_ai(cv_text, job_description):
    """Analyse le CV par rapport à l'offre d'emploi via Gemini."""
    
    # Configuration via les secrets Streamlit
    if "GEMINI_API_KEY" not in st.secrets:
        return {"score": 0, "verdict": "Clé API Gemini manquante dans les Secrets."}
        
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Modèle Flash (Rapide et gratuit dans les limites du quota)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    En tant qu'expert RH, analyse la pertinence de ce CV pour ce poste.
    
    POSTE : {job_description}
    CV : {cv_text}
    
    Réponds uniquement en JSON :
    {{
        "score": (0-100),
        "points_forts": [],
        "points_faibles": [],
        "verdict": "court résumé"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Nettoyage pour extraire le JSON
        txt = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(txt)
    except Exception as e:
        return {"score": 0, "verdict": f"Erreur technique : {str(e)}"}
