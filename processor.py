import streamlit as st
from datetime import datetime
from ai_engine import analyze_cv_with_ai
from supabase import create_client

# Initialisation unique du client Supabase pour plus de rapidité
supabase_op = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

def check_quota(user_id_or_ip):
    """Vérifie si l'utilisateur a encore des crédits IA pour aujourd'hui."""
    today = datetime.now().strftime('%Y-%m-%d')
    res = supabase_op.table("usage_logs").select("*", count="exact")\
        .eq("user_identifier", user_id_or_ip)\
        .eq("usage_date", today).execute()
    
    usage_count = res.count if res.count is not None else 0
    return usage_count < 5

def log_usage(user_id_or_ip):
    """Enregistre une utilisation dans la base de données."""
    supabase_op.table("usage_logs").insert({
        "user_identifier": user_id_or_ip,
        "usage_date": datetime.now().strftime('%Y-%m-%d')
    }).execute()

def process_matching(cv_text, job_requirements, user_info, local_ai_result=None):
    """
    Le cerveau de Zaxx : choisit entre l'IA locale et l'IA de secours.
    """
    # 1. TENTATIVE IA LOCALE (Priorité 1 : Gratuit et illimité)
    # Si le JavaScript a déjà renvoyé un résultat, on l'utilise directement
    if local_ai_result:
        return local_ai_result

    # 2. IA DE SECOURS (Priorité 2 : Gemini Cloud avec Quota)
    # Si pas d'IA locale, on vérifie si l'utilisateur n'a pas dépassé ses 5 essais
    if not check_quota(user_info):
        return {
            "score": 0, 
            "verdict": "❌ Limite journalière atteinte. Utilisez un appareil avec IA Native (Chrome/Gemini Nano) pour continuer gratuitement."
        }
    
    # Lancement de l'analyse via Gemini (ai_engine.py)
    result = analyze_cv_with_ai(cv_text, job_requirements)
    
    # On enregistre l'utilisation uniquement pour l'IA Cloud (car elle te coûte des crédits)
    log_usage(user_info)
    
    return result
