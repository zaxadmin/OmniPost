import streamlit as st
import pandas as pd
import random
from datetime import datetime
from supabase import create_client, Client
from typing import Dict, Optional, List
import requests
from pypdf import PdfReader  # Intégration pour la lecture des CV PDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="🚀")

# --- INIT SUPABASE ---
try:
    supabase: Client = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
except Exception as e:
    st.error(f"Erreur Supabase: {e}")
    st.stop()

# --- CONSTANTES ---
LANGUAGES = {
    "Français": {"flag": "🇫🇷", "country": "FR"},
    "English (US)": {"flag": "🇺🇸", "country": "US"},
    "Malgache": {"flag": "🇲🇬", "country": "MG"},
    "Español": {"flag": "🇪🇸", "country": "ES"},
    "Deutsch": {"flag": "🇩🇪", "country": "DE"},
    "Italiano": {"flag": "🇮🇹", "country": "IT"},
    "Português": {"flag": "🇵🇹", "country": "PT"},
    "Nederlands": {"flag": "🇳🇱", "country": "NL"},
    "Русский": {"flag": "🇷🇺", "country": "RU"},
    "日本語": {"flag": "🇯🇵", "country": "JP"},
    "한국어": {"flag": "🇰🇷", "country": "KR"},
    "中文": {"flag": "🇨🇳", "country": "CN"},
    "العربية": {"flag": "🇸🇦", "country": "SA"},
    "हिन्दी": {"flag": "🇮🇳", "country": "IN"},
    "Türkçe": {"flag": "🇹🇷", "country": "TR"},
    "Polski": {"flag": "🇵🇱", "country": "PL"},
    "Svenska": {"flag": "🇸🇪", "country": "SE"},
    "Tiếng Việt": {"flag": "🇻🇳", "country": "VN"},
    "ไทย": {"flag": "🇹🇭", "country": "TH"},
    "Ελληνικά": {"flag": "🇬🇷", "country": "GR"}
}

TEXTS = {
    "Français": {
        "login_title": "Bienvenue sur zipngo",
        "login_desc": "L'écosystème RH pour booster votre carrière.",
        "email": "Email",
        "send_link": "Envoyer le lien magique",
        "link_sent": "✅ Lien envoyé à {email} ! Vérifiez votre boîte mail.",
        "invalid_email": "Email invalide.",
        "welcome": "Bienvenue, {user} !",
        "logout": "Déconnexion",
        "dashboard": "Dashboard",
        "job_offer": "Créer une offre",
        "dispatch": "Diffuser une offre",
        "candidates": "Candidats pour mes offres",
        "video": "Visioconférence",
        "subscription": "Abonnement",
        "profile": "Mon profil",
        "my_cvs": "Mes CVs",
        "my_interviews": "Mes RDV visio",
        "improve": "Améliorer CV/Lettre",
        "ats_test": "Test ATS",
        "templates": "Templates CV",
        "apply_to_offer": "Postuler à une offre",
        "generate_offer": "Générer l'offre",
        "offer_created": "✅ Offre créée !",
        "select_countries": "Pays de diffusion",
        "save_countries": "Enregistrer",
        "send_email": "Envoyer par email",
        "dispatch_success": "✅ Diffusion réussie !",
        "upload_doc": "Télécharger un {type}",
        "upload_success": "✅ {type} téléchargé avec succès !",
        "email_recipients": "Adresses e-mails (séparées par des virgules)",
        "email_subject": "Objet de l'email",
        "improve_with_ai": "Améliorer avec IA",
        "improved_text": "{type} amélioré(e)",
        "download_improved": "Télécharger le {type} amélioré",
        "apply_template": "Appliquer un template",
        "ats_score": "Score ATS: {score}%",
        "ats_improved": "✅ Score amélioré à {score}% !",
        "select_template": "Choisissez un template",
        "schedule_interview": "Planifier un entretien",
        "accept": "Accepter",
        "refuse": "Refuser",
        "join": "Rejoindre l'entretien",
        "invitation_sent": "✅ Invitation enregistrée !",
        "subscription_title": "Gestion de vos accès & Offres Privilèges",
        "candidate_premium": "🚀 PASS PRIVILÈGE CANDIDAT (90 JOURS)",
        "employer_premium": "💼 PASS BUSINESS EMPLOYEUR (90 JOURS)",
        "extend_access": "PROLONGER MON ACCÈS POUR 3€",
        "become_premium": "DEVENIR PREMIUM POUR 39€",
        "candidates_title": "🔍 Candidatures pour vos offres",
        "candidates_desc": "Les candidats sont triés automatiquement par pertinence.",
        "no_candidates": "Aucune candidature pour le moment.",
        "candidate_score": "Score de correspondance: {score}%",
        "candidate_details": "Détails du candidat",
        "candidate_email": "Email: {email}",
        "candidate_skills": "Compétences: {skills}",
        "candidate_experience": "Expérience: {experience}",
        "candidate_cv": "CV: {cv_name}",
        "filter_drawer": "Filtrer par tiroir",
        "drawer_very_high": "🟢 Très bonne correspondance (90-100%)",
        "drawer_high": "🟡 Bonne correspondance (70-89%)",
        "drawer_medium": "🟠 Correspondance moyenne (50-69%)",
        "drawer_low": "🔴 Faible correspondance (<50%)",
        "all_candidates": "Tous les candidats",
        "contact_candidate": "Contacter le candidat",
        "view_cv": "Voir le CV",
        "profile_title": "👤 Mon profil candidat",
        "profile_desc": "Complétez votre profil pour être visible par les recruteurs.",
        "save_profile": "Enregistrer mon profil",
        "profile_saved": "✅ Profil enregistré avec succès !",
        "job_title": "Poste recherché *",
        "contract_type": "Type de contrat souhaité *",
        "location": "Localisation *",
        "country": "Pays",
        "city": "Ville",
        "remote": "100% à distance",
        "max_distance": "Distance maximale (km) (si non remote)",
        "salary_expectation": "Prétention salariale (€/an ou €/mois)",
        "licenses": "Permis",
        "languages": "Langues parlées",
        "profile_info": "Informations de profil",
        "no_profile": "Votre profil n'est pas encore complété.",
        "my_interviews_title": "🎥 Mes RDV visio",
        "no_interviews": "Aucun RDV programmé pour le moment.",
        "interview_status": "Statut: {status}",
        "interview_date": "📅 Date: {date}",
        "interview_time": "⏰ Heure: {time}",
        "interview_company": "Entreprise: {company}",
        "interview_job": "Poste: {job}",
        "apply_to_offer_title": "📩 Postuler à une offre",
        "select_offer": "Sélectionnez une offre",
        "apply_success": "✅ Candidature envoyée avec succès !",
        "already_applied": "Vous avez déjà postulé à cette offre.",
        "no_offers": "Aucune offre disponible pour le moment.",
        "footer_legal": "Mentions Légales",
        "footer_cgv": "CGV",
        "footer_copyright": "© 2026 zipngo | Créatrice : Liliane RAKOTOBE ✉️"
    },
    "English (US)": {
        "login_title": "Welcome to zipngo",
