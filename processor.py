import streamlit as st
from datetime import datetime
from ai_engine import analyze_cv_with_ai
from supabase import create_client

def check_quota(user_id_or_ip):
    """Vérifie si l'utilisateur a encore des crédits IA pour aujourd'hui."""
    supabase_op = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])
    today = datetime.now().strftime('%Y-%m-%d')
    
    # On compte les entrées dans une table 'usage_logs'
    res = supabase_op.table("usage_logs").select("*", count="exact")\
        .eq("user_identifier", user_id_or_ip)\
        .eq("usage_date", today).execute()
    
    usage_count = res.count if res.count is not None else 0
    return usage_count < 5  # Limite de 5 par jour

def log_usage(user_id_or_ip):
    """Enregistre une utilisation de l'IA de secours."""
    supabase_op = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])
    supabase_op.table("usage_logs").insert({
        "user_identifier": user_id_or_ip,
        "usage_date": datetime.now().strftime('%Y-%m-%d')
    }).execute()

def process_matching(cv_text, job_requirements, user_info):
    # 1. Tentative IA Locale (Illimitée car gratuite pour toi)
    # ... (code précédent pour window.ai)
    
    # 2. IA de Secours (Avec Limite)
    if not check_quota(user_info):
        return "❌ Limite journalière d'analyse IA atteinte. Réessayez demain ou utilisez un appareil compatible IA Native."
    
    # Lancement Gemini
    result = analyze_cv_with_ai(cv_text, job_requirements)
    log_usage(user_info)
    return result
