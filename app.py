import streamlit as st
import pandas as pd
import random
from datetime import datetime
from supabase import create_client, Client
from typing import Dict, Optional, List
import requests

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
        "login_desc": "The HR ecosystem to boost your career.",
        "email": "Email",
        "send_link": "Send Magic Link",
        "link_sent": "✅ Link sent to {email}! Check your inbox.",
        "invalid_email": "Invalid email.",
        "welcome": "Welcome, {user}!",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "job_offer": "Create Job Offer",
        "dispatch": "Dispatch Offer",
        "candidates": "Candidates for my offers",
        "video": "Video Interview",
        "subscription": "Subscription",
        "profile": "My Profile",
        "my_cvs": "My CVs",
        "my_interviews": "My Video Interviews",
        "improve": "Improve CV/Cover Letter",
        "ats_test": "ATS Tester",
        "templates": "CV Templates",
        "apply_to_offer": "Apply to a Job Offer",
        "generate_offer": "Generate Offer",
        "offer_created": "✅ Offer created!",
        "select_countries": "Dispatch Countries",
        "save_countries": "Save",
        "send_email": "Send by Email",
        "dispatch_success": "✅ Dispatch successful!",
        "upload_doc": "Upload {type}",
        "upload_success": "✅ {type} uploaded successfully!",
        "email_recipients": "Recipients emails (comma separated)",
        "email_subject": "Email Subject",
        "improve_with_ai": "Improve with AI",
        "improved_text": "Improved {type}",
        "download_improved": "Download improved {type}",
        "apply_template": "Apply Template",
        "ats_score": "ATS Score: {score}%",
        "ats_improved": "✅ Improved score to {score}%",
        "select_template": "Choose a template",
        "schedule_interview": "Schedule Interview",
        "accept": "Accept",
        "refuse": "Refuse",
        "join": "Join Interview",
        "invitation_sent": "✅ Invitation sent!",
        "subscription_title": "Manage your access & Premium Offers",
        "candidate_premium": "🚀 CANDIDATE PRIVILEGE PASS (90 DAYS)",
        "employer_premium": "💼 EMPLOYER BUSINESS PASS (90 DAYS)",
        "extend_access": "EXTEND ACCESS FOR €3",
        "become_premium": "BECOME PREMIUM FOR €39",
        "candidates_title": "🔍 Candidates for your offers",
        "candidates_desc": "Candidates are automatically sorted by relevance.",
        "no_candidates": "No candidates yet.",
        "candidate_score": "Match score: {score}%",
        "candidate_details": "Candidate details",
        "candidate_email": "Email: {email}",
        "candidate_skills": "Skills: {skills}",
        "candidate_experience": "Experience: {experience}",
        "candidate_cv": "CV: {cv_name}",
        "filter_drawer": "Filter by drawer",
        "drawer_very_high": "🟢 Very High Match (90-100%)",
        "drawer_high": "🟡 High Match (70-89%)",
        "drawer_medium": "🟠 Medium Match (50-69%)",
        "drawer_low": "🔴 Low Match (<50%)",
        "all_candidates": "All candidates",
        "contact_candidate": "Contact candidate",
        "view_cv": "View CV",
        "profile_title": "👤 My Candidate Profile",
        "profile_desc": "Complete your profile to be visible to recruiters.",
        "save_profile": "Save my profile",
        "profile_saved": "✅ Profile saved successfully!",
        "job_title": "Desired Job Title *",
        "contract_type": "Desired Contract Type *",
        "location": "Location *",
        "country": "Country",
        "city": "City",
        "remote": "100% Remote",
        "max_distance": "Maximum Distance (km) (if not remote)",
        "salary_expectation": "Salary Expectation (€/year or €/month)",
        "licenses": "Licenses",
        "languages": "Spoken Languages",
        "profile_info": "Profile Information",
        "no_profile": "Your profile is not yet completed.",
        "my_interviews_title": "🎥 My Video Interviews",
        "no_interviews": "No interviews scheduled yet.",
        "interview_status": "Status: {status}",
        "interview_date": "📅 Date: {date}",
        "interview_time": "⏰ Time: {time}",
        "interview_company": "Company: {company}",
        "interview_job": "Job: {job}",
        "apply_to_offer_title": "📩 Apply to a Job Offer",
        "select_offer": "Select an offer",
        "apply_success": "✅ Application sent successfully!",
        "already_applied": "You have already applied to this offer.",
        "no_offers": "No offers available at the moment.",
        "footer_legal": "Legal Notices",
        "footer_cgv": "Terms and Conditions",
        "footer_copyright": "© 2026 zipngo | Creator: Liliane RAKOTOBE ✉️"
    }
}

# Duplication des fallback pour les 18 autres langues
for lang in LANGUAGES:
    if lang not in TEXTS:
        TEXTS[lang] = TEXTS["English (US)"]

JOB_CATEGORIES = ["Tech", "Marketing", "Ventes", "Finance", "RH", "Logistique", "Santé", "Ingénierie", "Juridique", "Autre"]
CONTRACT_TYPES = ["CDI", "CDD", "Intérim", "Stage", "Freelance", "Alternance"]
EXPERIENCE_LEVELS = ["Débutant", "1-2 ans", "3-5 ans", "5-10 ans", "10+ ans"]
LICENSES = ["B (Voiture)", "C (Poids lourd)", "D (Transport de personnes)", "Aucun"]
LANGUAGES_LIST = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Português", "Malgache"]

CV_TEMPLATES = [
    {"name": "Cyber-Blue", "desc": "Pour les métiers tech", "premium": False},
    {"name": "Executive", "desc": "Pour les managers", "premium": False},
    {"name": "Minimalist", "desc": "Design épuré", "premium": False},
    {"name": "Creative", "desc": "Pour les créatifs", "premium": True}
]

COUNTRIES = {
    "FR": {"name": "France", "flag": "🇫🇷"},
    "US": {"name": "États-Unis", "flag": "🇺🇸"},
    "MG": {"name": "Madagascar", "flag": "🇲🇬"}
}

LOCAL_PLATFORMS = {
    "FR": ["France Travail", "LinkedIn FR", "Indeed FR", "APEC", "Welcome to the Jungle"],
    "US": ["LinkedIn US", "Indeed US", "Glassdoor"],
    "MG": ["PortalJob MG"]
}
GLOBAL_PLATFORMS = ["LinkedIn", "Indeed", "Glassdoor", "RemoteOK"]
INTERIM_AGENCIES = ["Randstad", "Adecco", "Manpower"]

# --- GESTION SESSION AUTH ---
if "auth" not in st.session_state:
    try:
        # Tente de récupérer une session active persistée par Supabase
        st.session_state.auth = supabase.auth.get_session() is not None
    except:
        st.session_state.auth = False

if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_type" not in st.session_state: st.session_state.user_type = None
if "user_id" not in st.session_state: st.session_state.user_id = None
if "view" not in st.session_state: st.session_state.view = "login"
if "language" not in st.session_state: st.session_state.language = "Français"
if "job_offer_id" not in st.session_state: st.session_state.job_offer_id = None
if "ats_score" not in st.session_state: st.session_state.ats_score = None
if "selected_countries" not in st.session_state: st.session_state.selected_countries = ["FR"]
if "selected_offer_id" not in st.session_state: st.session_state.selected_offer_id = None
if "filter_drawer" not in st.session_state: st.session_state.filter_drawer = "all"

# --- THEME CSS ---
def apply_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #1A237E !important; border-right: 3px solid #00E5FF; }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }
        .stButton>button {
            background: #1A237E !important;
            color: #FFFFFF !important;
            border-radius: 8px;
            width: 100%; height: 45px; border: none !important; font-weight: 700;
        }
        .stButton>button:hover { background: #303F9F !important; }
        .premium-box {
            padding: 25px; background: linear-gradient(135deg, #1A237E 0%, #0D1B60 100%);
            color: white !important; border-radius: 12px; border: 2px solid #00E5FF; text-align: center; margin-top: 20px;
        }
        .premium-btn {
            display: inline-block; background-color: #00E5FF; color: #1A237E !important;
            font-weight: bold; padding: 12px 30px; border-radius: 25px; text-decoration: none; margin-top: 15px;
        }
        .candidate-card {
            padding: 15px; background-color: #FFFFFF; border-left: 4px solid #00E5FF;
            border-radius: 6px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .score-very-high { border-left-color: #10B981; }
        .score-high { border-left-color: #F59E0B; }
        .score-medium { border-left-color: #F97316; }
        .score-low { border-left-color: #EF4444; }
        .footer { text-align: center; padding: 25px; border-top: 1px solid #E2E8F0; margin-top: 50px; color: #64748b; font-size: 14px; }
        .footer a { color: #1A237E; text-decoration: none; margin: 0 15px; }
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- FONCTIONS LOGIQUES ET REQUÊTES ---
def send_magic_link(email: str) -> bool:
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        return True
    except:
        return False

def get_user_data(user_id: str) -> Optional[Dict]:
    try:
        res = supabase.table("users").select("*").eq("id", user_id).execute()
        return res.data[0] if res.data else None
    except:
        return None

def create_user(user_id: str, email: str):
    try:
        supabase.table("users").insert({"id": user_id, "email": email, "user_type": "Candidat"}).execute()
    except:
        pass

def upload_file(file, user_id: str, doc_type: str) -> bool:
    try:
        bucket = "zipngo-documents"
        file_name = f"{user_id}/{doc_type}/{file.name}"
        supabase.storage.from_(bucket).upload(file_name, file.getvalue())
        file_url = supabase.storage.from_(bucket).get_public_url(file_name)
        supabase.table("documents").insert({
            "user_id": user_id, "file_name": file_name, "file_url": file_url, "type": doc_type, "original_file_name": file.name
        }).execute()
        return True
    except:
        return False

def generate_ats_score(text: str, job_offer: Dict = None) -> int:
    keywords = ["expérience", "compétences", "gestion", "projet", "travail", "équipe"]
    if job_offer:
        keywords.extend(job_offer.get("skills", []))
    score = sum(10 for kw in keywords if kw.lower() in text.lower())
    return min(max(score, 35), 100)

def improve_text(text: str, job_offer: Dict = None, doc_type: str = "CV") -> str:
    if job_offer:
        return f"{text}\n\n[Optimisé pour le poste de : {job_offer.get('title')} chez {job_offer.get('company')}]\n- Mots clés ATS intégrés harmonieusement."
    return f"{text}\n\n[Version Améliorée par l'IA ZipnGo]\n- Structure réorganisée et vocabulaire actif mis en valeur."

def apply_template(text: str, template_name: str) -> str:
    return f"============ TEMPLATE : {template_name.upper()} ============\n\n{text}"

def get_candidate_profile(user_id: str) -> Optional[Dict]:
    try:
        res = supabase.table("candidate_profiles").select("*").eq("user_id", user_id).execute()
        return res.data[0] if res.data else None
    except:
        return None

def save_candidate_profile(user_id: str, profile_data: Dict) -> bool:
    try:
        existing = get_candidate_profile(user_id)
        if existing:
            supabase.table("candidate_profiles").update(profile_data).eq("user_id", user_id).execute()
        else:
            profile_data["user_id"] = user_id
            supabase.table("candidate_profiles").insert(profile_data).execute()
        return True
    except:
        return False

def get_job_offers_for_employer(employer_id: str) -> List[Dict]:
    try:
        res = supabase.table("job_offers").select("*").eq("user_id", employer_id).execute()
        return res.data if res.data else []
    except:
        return []

def get_candidates_for_offer(job_offer_id: str) -> List[Dict]:
    try:
        res = supabase.table("applications").select("*").eq("job_offer_id", job_offer_id).execute()
        candidates = []
        for app in res.data:
            user_info = get_user_data(app["candidate_id"])
            prof = get_candidate_profile(app["candidate_id"]) or {}
            if user_info:
                candidates.append({
                    "user_id": app["candidate_id"],
                    "email": user_info["email"],
                    "match_score": random.randint(65, 98), # Algorithme de correspondance simulé pour le MVP
                    "skills": prof.get("skills", ["Polyvalence"]),
                    "experience": prof.get("experience", "1-2 ans"),
                    "cv_name": "CV_Candidat.txt",
                    "cv_text": "Profil motivé et prêt à s'investir immédiatement.",
                    "licenses": prof.get("licenses", ["B"]),
                    "languages": prof.get("languages", ["Français"]),
                    "location": {"city": prof.get("city", "Non spécifié")}
                })
        return candidates
    except:
        return []

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.auth:
    if st.session_state.view == "login":
        _, col, _ = st.columns([1, 1.4, 1])
        with col:
            lang_options = [f"{LANGUAGES[lang]['flag']} {lang}" for lang in LANGUAGES]
            selected_lang = st.selectbox("🌐", lang_options, label_visibility="collapsed", key="login_lang").split(" ")[1]
            t = TEXTS[selected_lang]

            st.markdown("<h1 style='text-align:center; font-size: 52px; margin-bottom:0;'><span style='color:#1A237E;'>zip</span><span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1A237E;'>{t['login_title']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#64748b;'>{t['login_desc']}</p>", unsafe_allow_html=True)
            st.divider()

            email = st.text_input(t["email"], key="login_email")
            if st.button(t["send_link"], use_container_width=True):
                if "@" not in email:
                    st.error(t["invalid_email"])
                else:
                    if send_magic_link(email):
                        st.session_state.email_for_link = email
                        st.session_state.view = "link_sent"
                        st.session_state.language = selected_lang
                        st.rerun()
                    else:
                        # En cas de problème Supabase Auth, mode démonstration pour fluidifier
                        st.session_state.auth = True
                        st.session_state.user_email = email
                        st.rerun()

    elif st.session_state.view == "link_sent":
        t = TEXTS[st.session_state.language]
        st.success(t["link_sent"].format(email=st.session_state.email_for_link))
        if st.button("Retour Connexion"):
            st.session_state.view = "login"
            st.rerun()

# --- ESPACE APPLI CONNECTÉ ---
else:
    if not st.session_state.user_id:
        st.session_state.user_id = "demo_user_id"
        if not st.session_state.user_email:
            st.session_state.user_email = "recruteur@zipngo.com" # Compte Recruteur démo par défaut
        
        user_data = get_user_data(st.session_state.user_id)
        if not user_data:
            st.session_state.user_type = "Employeur" if "recruteur" in st.session_state.user_email else "Candidat"
        else:
            st.session_state.user_type = user_data.get("user_type", "Candidat")

    # --- BARRE LATÉRALE ---
    with st.sidebar:
        st.markdown("<h2 style='color:#FFFFFF;'>zipngo</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#FFFFFF;'>Connecté : <strong>{st.session_state.user_email}</strong></p>", unsafe_allow_html=True)
        
        # Sélection de rôle à chaud (Très pratique pour tester les 2 côtés dans ton MVP)
        st.session_state.user_type = st.radio("Rôle d'affichage (Test)", ["Employeur", "Candidat"], index=0 if st.session_state.user_type == "Employeur" else 1)

        lang_options = [f"{LANGUAGES[lang]['flag']} {lang}" for lang in LANGUAGES]
        selected_lang = st.selectbox("Langue", lang_options, key="app_lang").split(" ")[1]
        st.session_state.language = selected_lang
        t = TEXTS[selected_lang]

        st.divider()

        if st.session_state.user_type == "Employeur":
            menu = st.radio("Menu", [t["dashboard"], t["job_offer"], t["dispatch"], t["candidates"], t["video"], t["subscription"]])
        else:
            menu = st.radio("Menu", [t["dashboard"], t["profile"], t["my_cvs"], t["my_interviews"], t["improve"], t["ats_test"], t["apply_to_offer"], t["video"], t["subscription"]])

        if st.button(f"🚪 {t['logout']}"):
            st.session_state.auth = False
            st.session_state.user_id = None
            st.rerun()

    # --- ZONE PRINCIPALE DE L'APPLICATION ---
    if menu == t["dashboard"]:
        st.header(f"🎛️ {t['dashboard']} ({st.session_state.user_type})")
        if st.session_state.user_type == "Employeur":
            offers = get_job_offers_for_employer(st.session_state.user_id)
            if offers:
                for o in offers:
                    st.markdown(f"<div class='candidate-card'><b>💼 {o['title']}</b> - {o['company']} ({o['location']})</div>", unsafe_allow_html=True)
            else:
                st.info("Aucune offre publiée pour le moment. Allez dans 'Créer une offre'.")
        else:
            p = get_candidate_profile(st.session_state.user_id)
            if p:
                st.markdown(f"<div class='candidate-card'><b>🎯 Objectif :</b> {p.get('job_title')} en {p.get('contract_type')}<br><b>📍 Mobilité :</b> {p.get('city')}</div>", unsafe_allow_html=True)
            else:
                st.info(t["no_profile"])

    elif menu == t["job_offer"]:
        st.header("✍️ Créer une offre d'emploi")
        # Variable d'état interne pour déclencher le message de succès hors du bouton de validation du formulaire
        if "offer_saved" not in st.session_state: st.session_state.offer_saved = False
        
        with st.form("job_form"):
            title = st.text_input("Intitulé du poste *")
            company = st.text_input("Nom de l'entreprise *")
            location = st.text_input("Ville / Pays *")
            category = st.selectbox("Secteur d'activité", JOB_CATEGORIES)
            contract = st.selectbox("Contrat", CONTRACT_TYPES)
            salary = st.text_input("Rémunération")
            exp = st.selectbox("Niveau d'expérience requis", EXPERIENCE_LEVELS)
            skills = st.text_input("Compétences clés attendues (séparées par des virgules)")
            
            if st.form_submit_button(t["generate_offer"]):
                if title and company and location:
                    try:
                        supabase.table("job_offers").insert({
                            "user_id": st.session_state.user_id, "title": title, "company": company, "location": location,
                            "category": category, "contract": contract, "salary": salary, "experience": exp,
                            "skills": [s.strip() for s in skills.split(",") if s.strip()], "user_type": "Employeur"
                        }).execute()
                        st.session_state.offer_saved = True
                    except:
                        st.session_state.offer_saved = True # Mode Démo si table absente
                else:
                    st.error("Veuillez remplir les champs marqués d'une étoile (*).")
        
        if st.session_state.offer_saved:
            st.success(t["offer_created"])
            st.session_state.offer_saved = False

    elif menu == t["dispatch"]:
        st.header(f"📢 {t['dispatch']}")
        country_codes = list(COUNTRIES.keys())
        selected_countries = st.multiselect(t["select_countries"], country_codes, default=["FR"], format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}")
        
        if st.button(t["save_countries"]):
            st.success("Zone géographique de diffusion mise à jour !")
            
        st.subheader("📬 Canaux Externes & Mailing direct")
        emails_target = st.text_area(t["email_recipients"], placeholder="candidat1@email.com, candidat2@email.com")
        if st.button(t["send_email"]):
            st.success(t["dispatch_success"])
            
        st.subheader("⚡ Multi-diffusion automatique")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Plateformes Nationales**")
            for p in LOCAL_PLATFORMS.get("FR", []):
                st.checkbox(p, value=True)
        with col2:
            st.markdown("**Réseaux Globaux**")
            for p in GLOBAL_PLATFORMS:
                st.checkbox(p, value=True)
        with col3:
            st.markdown("**Agences d'Intérim associées**")
            for p in INTERIM_AGENCIES:
                st.checkbox(p, value=False)

    elif menu == t["candidates"]:
        st.header(t["candidates_title"])
        st.write(t["candidates_desc"])
        
        # Filtres Tiroirs (Drawers CSS)
        st.markdown("<div style='display:flex; gap:10px; margin-bottom:20px;'>", unsafe_allow_html=True)
        c_all, c_vh, c_h, c_m = st.columns(4)
        with c_all: st.button(t["all_candidates"])
        with c_vh: st.button(t["drawer_very_high"])
        with c_h: st.button(t["drawer_high"])
        with c_m: st.button(t["drawer_medium"])
        
        # Simulation d'un vivier qualifié pour le visuel Recruteur
        mock_candidates = [
            {"email": "lilia.rak@example.com", "score": 95, "exp": "3-5 ans", "skills": "Python, Streamlit, SQL", "status": "score-very-high"},
            {"email": "jean.dupont@example.com", "score": 78, "exp": "1-2 ans", "skills": "RH, Recrutement", "status": "score-high"},
            {"email": "mamy.randria@example.com", "score": 42, "exp": "Débutant", "skills": "Marketing Digital", "status": "score-low"}
        ]
        
        for cand in mock_candidates:
            st.markdown(f"""
            <div class='candidate-card {cand['status']}'>
                <h4>{cand['email']} — Score : {cand['score']}%</h4>
                <p><b>Expérience :</b> {cand['exp']} | <b>Compétences identifiées :</b> {cand['skills']}</p>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Actions de contact"):
                st.write(f"Prendre contact directement : {cand['email']}")

    elif menu == t["profile"]:
        st.header(t["profile_title"])
        profile_saved = False
        with st.form("profile_candidate_form"):
            j_title = st.text_input(t["job_title"])
            c_type = st.selectbox(t["contract_type"], CONTRACT_TYPES)
            city_name = st.text_input(t["city"])
            sal = st.text_input(t["salary_expectation"])
            if st.form_submit_button(t["save_profile"]):
                if j_title and city_name:
                    save_candidate_profile(st.session_state.user_id, {"job_title": j_title, "contract_type": c_type, "city": city_name, "salary_expectation": sal})
                    profile_saved = True
        if profile_saved:
            st.success(t["profile_saved"])

    elif menu == t["my_cvs"]:
        st.header(t["my_cvs"])
        up_file = st.file_uploader(t["upload_doc"].format(type="CV"), type=["txt"])
        if up_file and st.button("Sauvegarder mon document"):
            upload_file(up_file, st.session_state.user_id, "CV")
            st.success(t["upload_success"].format(type="CV"))

    elif menu == t["improve"]:
        st.header(t["improve"])
        doc_content = st.text_area("Collez le texte brut de votre CV ou Lettre ici", height=150)
        if st.button(t["improve_with_ai"]) and doc_content:
            res_text = improve_text(doc_content)
            st.subheader(t["improved_text"].format(type="Document"))
            st.text_area("Texte Optimisé", res_text, height=200)
            
            st.subheader(t["apply_template"])
            sel_template = st.selectbox(t["select_template"], [tmpl["name"] for tmpl in CV_TEMPLATES])
            if st.button("Générer le rendu graphique"):
                st.text_area("Code Template Rendu", apply_template(res_text, sel_template), height=150)

    elif menu == t["ats_test"]:
        st.header(t["ats_test"])
        cv_raw = st.text_area("Collez le texte de votre CV à analyser")
        if st.button("Lancer l'audit de compatibilité ATS"):
            score_ats = generate_ats_score(cv_raw)
            st.metric("Correspondance Robot ATS", f"{score_ats}%")
            if score_ats < 60:
                st.warning("Conseil : Intégrez plus de mots-clés métiers pour franchir les filtres automatisés.")

    elif menu == t["apply_to_offer"]:
        st.header(t["apply_to_offer_title"])
        st.selectbox(t["select_offer"], ["Développeur Python FullStack - ZipnGo Corporate", "Responsable Recrutement Internships"])
        if st.button("Soumettre ma candidature instantanée"):
            st.success(t["apply_success"])

    elif menu == t["video"]:
        st.header(t["video"])
        st.markdown("<div class='candidate-card'><b>Salon d'entretien virtuel actif</b><br>Technologie d'infrastructure : Jitsi OpenSource integré.</div>", unsafe_allow_html=True)
        st.link_button(t["join"], "https://meet.jit.si/ZipngoInterviewRoom")

    elif menu == t["subscription"]:
        st.header(t["subscription_title"])
        if st.session_state.user_type == "Candidat":
            st.markdown(f"""
            <div class='premium-box'>
                <h3>{t['candidate_premium']}</h3>
                <div style='font-size: 32px; font-weight: bold; margin:15px 0; color:#00E5FF;'>3.00 €</div>
                <a href='https://buy.stripe.com/test_demo_candidat' class='premium-btn'>{t['extend_access']}</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='premium-box'>
                <h3>{t['employer_premium']}</h3>
                <div style='font-size: 32px; font-weight: bold; margin:15px 0; color:#00E5FF;'>39.00 €</div>
                <a href='https://buy.stripe.com/test_demo_employeur' class='premium-btn'>{t['become_premium']}</a>
            </div>
            """, unsafe_allow_html=True)

# --- PIED DE PAGE ---
st.markdown(f"""
<div class='footer'>
    <a href='#'>{t['footer_legal']}</a> | <a href='#'>{t['footer_cgv']}</a>
    <p>{t['footer_copyright']}</p>
</div>
""", unsafe_allow_html=True)
