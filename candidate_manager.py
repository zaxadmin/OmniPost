import streamlit as st
from supabase import create_client

def get_zip_client():
    # Connexion au projet ZIP
    return create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])

def notify_candidate(candidate_email, message_key):
    # Utilise ton i18n_manager pour le message
    from i18n_manager import OmniPostI18n
    lang = "fr" # On pourrait le récupérer dynamiquement
    i18n = OmniPostI18n(lang)
    
    body = i18n.get_text(message_key)
    
    # Ici, tu pourrais intégrer un service d'envoi d'email (SendGrid, Mailgun)
    # Pour l'instant, on simule l'envoi
    st.info(f"📧 Notification envoyée à {candidate_email} : {body[:30]}...")

def get_candidates_by_score(min_score=80):
    client = get_zip_client()
    # On récupère les candidats qui ont un bon matching
    try:
        res = client.table("cv_data").select("*").gte("score", min_score).execute()
        return res.data
    except:
        return []
