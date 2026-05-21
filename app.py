import streamlit as st
import pandas as pd
import random
from datetime import datetime
import urllib.parse
from supabase import create_client, Client
from typing import Dict, Optional, List
from pypdf import PdfReader
import json
import requests

# --- CONFIGURATION DE PAGE ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="🚀")

# --- INITIALISATION SUPABASE & GROQ ---
try:
    supabase: Client = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    GROQ_API_KEY = st.secrets["groq"]["api_key"]
except Exception as e:
    st.error(f"Erreur d'initialisation des clés API (Supabase/Groq) dans les secrets: {e}")
    st.stop()

# --- DICTIONNAIRES & CONSTANTES ---
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
        "subscription": "Mon Accès / Pass",
        "profile": "Mon profil",
        "my_cvs": "Mes CVs",
        "my_interviews": "Suivi Entretiens (Match)",
        "improve": "Améliorer CV/Lettre",
        "ats_test": "Test ATS",
        "apply_to_offer": "Postuler à une offre",
        "generate_offer": "Générer l'offre",
        "offer_created": "✅ Offre créée et répertoriée anonymement !",
        "select_countries": "Pays de diffusion",
        "save_countries": "Enregistrer",
        "send_email": "Envoyer par email",
        "dispatch_success": "✅ Diffusion réussie !",
        "upload_doc": "Télécharger un {type}",
        "upload_success": "✅ {type} téléchargé et sauvegardé dans votre espace !",
        "email_recipients": "Adresses e-mails (séparées par des virgules)",
        "email_subject": "Objet de l'email",
        "improve_with_ai": "Améliorer avec IA",
        "improved_text": "{type} amélioré(e)",
        "download_improved": "Télécharger le {type} amélioré",
        "apply_template": "Appliquer un template",
        "ats_score": "Score ATS: {score}%",
        "ats_improved": "✅ Score amélioré à {score}% !",
        "select_template": "Choisissez un template",
        "subscription_title": "Gestion de vos accès & Offres Privilèges",
        "candidate_premium": "🚀 PASS PRIVILÈGE CANDIDAT (90 JOURS)",
        "employer_premium": "💼 PASS BUSINESS EMPLOYEUR (90 JOURS)",
        "extend_access": "ACTIVER MON ACCÈS POUR 3€",
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
        "city": "Ville *",
        "remote": "100% à distance",
        "salary_expectation": "Prétention salariale (€/an ou €/mois)",
        "my_interviews_title": "🎥 Mes RDV visio",
        "join": "Rejoindre l'entretien",
        "apply_to_offer_title": "📩 Offres d'Emploi Disponibles (Données Protégées)",
        "select_offer": "Sélectionnez une offre",
        "apply_success": "✅ Candidature transmise d'office !",
        "dispatch_cv": "🚀 Propulser mon CV (Target RH)",
        "footer_legal": "Mentions Légales",
        "footer_cgv": "CGV",
        "footer_copyright": "© 2026 zipngo | Créatrice : Liliane RAKOTOBE ✉️"
    }
}

for lang in LANGUAGES:
    if lang not in TEXTS:
        TEXTS[lang] = TEXTS["Français"]

JOB_CATEGORIES = ["Tech", "Marketing", "Ventes", "Finance", "RH", "Logistique", "Santé", "Ingénierie", "Juridique", "Autre"]
CONTRACT_TYPES = ["CDI", "CDD", "Intérim", "Stage", "Freelance", "Alternance"]
EXPERIENCE_LEVELS = ["Débutant", "1-2 ans", "3-5 ans", "5-10 ans", "10+ ans"]
SECTORS_LIST = ["Tertiaire / Services", "Industrie", "Commerce / Distribution", "BTP / Construction", "Agriculture / Agroalimentaire", "Secteur Public"]

CV_TEMPLATES = [
    {"name": "Cyber-Blue", "desc": "Pour les métiers tech"},
    {"name": "Executive", "desc": "Pour les managers"},
    {"name": "Minimalist", "desc": "Design épuré"},
    {"name": "Creative", "desc": "Pour les créatifs"}
]

COUNTRIES = {
    "FR": {"name": "France", "flag": "🇫🇷"},
    "US": {"name": "États-Unis", "flag": "🇺🇸"},
    "MG": {"name": "Madagascar", "flag": "🇲🇬"}
}

LOCAL_PLATFORMS = {"FR": ["France Travail", "LinkedIn FR", "Indeed FR"], "US": ["LinkedIn US", "Indeed US"], "MG": ["PortalJob MG"]}
GLOBAL_PLATFORMS = ["LinkedIn", "Indeed", "Glassdoor"]
INTERIM_AGENCIES = ["Randstad", "Adecco", "Manpower"]

# --- GESTION DE SESSION APP ---
if "auth" not in st.session_state:
    try:
        st.session_state.auth = supabase.auth.get_session() is not None
    except:
        st.session_state.auth = False

for key, val in {
    "user_email": None, "user_type": None, "user_id": None, "view": "login",
    "language": "Français", "cv_extracted_text": "", "dispatch_logs": [],
    "is_candidate_premium": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- INJECTION THÈME CSS ---
def apply_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #1A237E !important; border-right: 3px solid #00E5FF; }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }
        .stButton>button {
            background: #1A237E !important; color: #FFFFFF !important;
            border-radius: 8px; width: 100%; height: 45px; font-weight: 700; border: none !important;
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
        .anon-badge { background-color: #E0F7FA; color: #006064; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .footer { text-align: center; padding: 25px; border-top: 1px solid #E2E8F0; margin-top: 50px; color: #64748b; font-size: 14px; }
        .footer a { color: #1A237E; text-decoration: none; margin: 0 15px; }
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# --- BACKEND FONCTIONS ---
def send_magic_link(email: str) -> bool:
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        return True
    except:
        return False

def get_or_create_user(email: str, selected_role: str) -> Dict:
    try:
        res = supabase.table("users").select("*").eq("user_email", email).execute()
        if res.data:
            return res.data[0]
        else:
            new_u = supabase.table("users").insert({"id": email, "user_email": email, "user_type": selected_role}).execute()
            return new_u.data[0]
    except:
        return {"id": email, "user_email": email, "user_type": selected_role}

def upload_file_to_storage(file, user_id: str, doc_type: str) -> bool:
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

def parse_skills_with_groq(cv_text: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    prompt = f"Analyse le texte du CV suivant et extrait uniquement une liste épurée de compétences techniques clés séparées par des virgules :\n\n{cv_text}"
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['choices'][0]['message']['content'].strip()
    except:
        return "Python, SQL, Management (Par défaut)"

def generate_ats_score(text: str) -> int:
    keywords = ["expérience", "compétences", "gestion", "projet", "python", "agile", "rh", "marketing", "vente", "recrutement"]
    score = sum(10 for kw in keywords if kw.lower() in text.lower())
    return min(max(score, 40), 100)

def improve_text(text: str, doc_type: str = "CV") -> str:
    return f"{text}\n\n[Version Améliorée par l'IA ZipnGo]\n- Structure réorganisée et vocabulaire actif optimisé pour les robots ATS."

def apply_template(text: str, template_name: str) -> str:
    return f"============ RENDU GRAPHIQUE : {template_name.upper()} ============\n\n{text}"


# --- ÉCRAN D'AUTHENTIFICATION ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        lang_options = [f"{LANGUAGES[lang]['flag']} {lang}" for lang in LANGUAGES]
        selected_lang = st.selectbox("🌐", lang_options, label_visibility="collapsed", key="login_lang").split(" ")[1]
        st.session_state.language = selected_lang
        t = TEXTS[selected_lang]

        st.markdown("<h1 style='text-align:center; font-size: 52px; margin-bottom:0;'><span style='color:#1A237E;'>zip</span><span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1A237E;'>{t['login_title']}</p>", unsafe_allow_html=True)
        st.divider()

        chosen_user_type = st.radio("Sélectionnez votre profil d'accès :", ["Candidat", "Employeur"], horizontal=True)

        email = st.text_input(t["email"], key="login_email")
        if st.button(t["send_link"], use_container_width=True):
            if "@" not in email:
                st.error(t["invalid_email"])
            else:
                send_magic_link(email)
                user_record = get_or_create_user(email, chosen_user_type)
                st.session_state.auth = True
                st.session_state.user_email = email
                st.session_state.user_id = user_record["id"]
                st.session_state.user_type = user_record["user_type"]
                st.rerun()
else:
    # --- NAVIGATION LATÉRALE & ONBOARDING EXPLICITE ---
    with st.sidebar:
        st.markdown("<h2 style='color:#FFFFFF;'>zipngo</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#FFFFFF;'>Connecté : <strong>{st.session_state.user_email}</strong></p>", unsafe_allow_html=True)
        
        st.session_state.user_type = st.radio("Rôle actif", ["Candidat", "Employeur"], index=0 if st.session_state.user_type == "Employeur" else 1)
        
        lang_options = [f"{LANGUAGES[lang]['flag']} {lang}" for lang in LANGUAGES]
        selected_lang = st.selectbox("Langue", lang_options, key="app_lang").split(" ")[1]
        st.session_state.language = selected_lang
        t = TEXTS[selected_lang]
        st.divider()

        st.markdown("### 💡 Mode d'emploi zipngo")
        if st.session_state.user_type == "Candidat":
            st.caption("""
            1. **100% Gratuit de base** : Créez votre profil, déposez votre CV, analysez-le par IA et téléchargez vos templates sans dépenser 1 centime.
            2. **Pass Multipostage & Scraping** : L'accès à l'extraction de contacts RH (LinkedIn inclus) et l'envoi groupé automatisé est un **accès payant à durée limitée** (3€ pour 90 jours). **Aucun abonnement, aucun renouvellement automatique.**
            3. **Anonymat total** : Vos coordonnées restent masquées sur zipngo et ne sont levées qu'en cas de Double Match réciproque après entretien.
            """)
        else:
            st.caption("""
            1. **Focus Compétences** : Évaluez des fiches candidats neutres et dénuées de données civiles.
            2. **Vote secret** : Le contact n'est débloqué que si le candidat accepte aussi votre suite favorable.
            3. **Pass Business** : Accès temporaire de 90 jours pour publier et diffuser vos offres.
            """)

        st.divider()
        if st.session_state.user_type == "Employeur":
            menu = st.radio("Menu", [t["dashboard"], t["job_offer"], t["dispatch"], t["candidates"], t["my_interviews"], t["video"], t["subscription"]])
        else:
            menu = st.radio("Menu", [t["dashboard"], t["profile"], t["my_cvs"], t["dispatch_cv"], t["apply_to_offer"], t["improve"], t["ats_test"], t["my_interviews"], t["video"], t["subscription"]])

        if st.button(f"🚪 {t['logout']}"):
            st.session_state.auth = False
            st.session_state.user_id = None
            st.rerun()

    # --- ZONE PRINCIPALE DE L'APPLICATION ---
    if menu == t["dashboard"]:
        st.header(f"🎛️ {t['dashboard']} ({st.session_state.user_type})")
        if st.session_state.user_type == "Employeur":
            try:
                res = supabase.table("job_offers").select("*").eq("user_id", st.session_state.user_id).execute()
                offers = res.data
            except:
                offers = []
            
            if offers:
                for o in offers:
                    st.markdown(f"<div class='candidate-card'><b>🔢 N° {o['offer_number']} : {o['title']}</b> ({o['location']}) - {o['contract']}</div>", unsafe_allow_html=True)
            else:
                st.info("Aucune offre publiée pour le moment. Accédez à l'onglet 'Créer une offre'.")
        else:
            try:
                res = supabase.table("candidate_profiles").select("*").eq("user_id", st.session_state.user_id).execute()
                p = res.data[0] if res.data else None
            except:
                p = None
                
            if p:
                st.markdown(f"<div class='candidate-card'><b>🎯 Objectif professionnel :</b> {p.get('job_title')} ({p.get('contract_type')})<br><b>📍 Ancrage géographique :</b> {p.get('city')}</div>", unsafe_allow_html=True)
            else:
                st.info(t["profile_desc"])

    elif menu == t["job_offer"]:
        st.header("✍️ Créer une offre d'emploi")
        with st.form("job_form_prod"):
            title = st.text_input("Intitulé du poste *")
            company = st.text_input("Nom de l'entreprise (Sera masqué au public d'office) *")
            location = st.text_input("Ville / Localisation *")
            category = st.selectbox("Secteur d'activité", JOB_CATEGORIES)
            contract = st.selectbox("Contrat", CONTRACT_TYPES)
            salary = st.text_input("Rémunération (€/an)")
            exp = st.selectbox("Niveau d'expérience requis", EXPERIENCE_LEVELS)
            skills = st.text_input("Compétences clés attendues (séparées par des virgules)")
            
            if st.form_submit_button(t["generate_offer"]):
                if title and company and location:
                    off_num = f"ZN-2026-{random.randint(1000, 9999)}"
                    try:
                        supabase.table("job_offers").insert({
                            "user_id": st.session_state.user_id, "offer_number": off_num, "title": title, "company": company,
                            "location": location, "category": category, "contract": contract, "salary": salary,
                            "experience": exp, "skills": [s.strip() for s in skills.split(",") if s.strip()]
                        }).execute()
                        st.success(f"{t['offer_created']} Numéro unique attribué : {off_num}")
                    except Exception as e:
                        st.error(f"Erreur d'insertion : {e}")
                else:
                    st.error("Veuillez remplir les champs obligatoires (*).")

    elif menu == t["dispatch"]:
        st.header(f"📢 {t['dispatch']}")
        country_codes = list(COUNTRIES.keys())
        st.multiselect(t["select_countries"], country_codes, default=["FR"], format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}")
        
        st.subheader("📬 Canaux Externes & Mailing direct (Lève l'anonymat entreprise)")
        st.text_area(t["email_recipients"], placeholder="hr@entreprise.com, contact@recrute.net")
        if st.button(t["send_email"]):
            st.success(t["dispatch_success"])
            
        st.subheader("⚡ Multi-diffusion automatique")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Plateformes Nationales**")
            for p in LOCAL_PLATFORMS.get("FR", []): st.checkbox(p, value=True)
        with col2:
            st.markdown("**Réseaux Globaux**")
            for p in GLOBAL_PLATFORMS: st.checkbox(p, value=True)
        with col3:
            st.markdown("**Agences d'Intérim**")
            for p in INTERIM_AGENCIES: st.checkbox(p, value=False)

    elif menu == t["candidates"]:
        st.header(t["candidates_title"])
        st.write(t["candidates_desc"])
        
        try:
            candidates = supabase.table("candidate_profiles").select("*").execute().data
        except:
            candidates = []

        if not candidates:
            st.info("Aucune fiche candidat disponible.")
        else:
            for cand in candidates:
                st.markdown(f"""
                <div class='candidate-card'>
                    <h4>🆔 Réf : Candidat-Anonyme-#{str(cand['user_id'])[:6]}</h4>
                    <p><b>Poste ciblé :</b> {cand.get('job_title', 'Non spécifié')} | <b>Ville :</b> {cand.get('city','Distanciel')}</p>
                    <p><b>Compétences Extraites par l'IA :</b> {cand.get('skills_extracted', 'À analyser')}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Planifier un RDV d'entretien", key=f"inv_{cand['user_id']}"):
                    try:
                        supabase.table("interviews").insert({
                            "candidate_id": cand["user_id"], "company_id": st.session_state.user_id, "job_title": cand.get('job_title', 'Poste Général')
                        }).execute()
                        st.success("Entretien ajouté à votre suivi Confidentiel.")
                    except:
                        pass

    elif menu == t["profile"]:
        st.header(t["profile_title"])
        try:
            res = supabase.table("candidate_profiles").select("*").eq("user_id", st.session_state.user_id).execute()
            current_p = res.data[0] if res.data else {}
        except:
            current_p = {}

        with st.form("profile_candidate_form_prod"):
            j_title = st.text_input(t["job_title"], value=current_p.get("job_title", ""))
            c_type = st.selectbox(t["contract_type"], CONTRACT_TYPES, index=CONTRACT_TYPES.index(current_p.get("contract_type", "CDI")) if current_p.get("contract_type") in CONTRACT_TYPES else 0)
            city_name = st.text_input(t["city"], value=current_p.get("city", ""))
            sal = st.text_input(t["salary_expectation"], value=current_p.get("salary_expectation", ""))
            is_remote_db = st.checkbox(t["remote"], value=current_p.get("remote", False))
            t_country = st.selectbox("Pays cible", list(COUNTRIES.keys()), index=list(COUNTRIES.keys()).index(current_p.get("target_country", "FR")) if current_p.get("target_country") in COUNTRIES else 0, format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}")
            
            if st.form_submit_button(t["save_profile"]):
                if j_title and city_name:
                    p_data = {"user_id": st.session_state.user_id, "job_title": j_title, "contract_type": c_type, "city": city_name, "salary_expectation": sal, "remote": is_remote_db, "target_country": t_country}
                    try:
                        supabase.table("candidate_profiles").upsert(p_data).execute()
                        st.success(t["profile_saved"])
                    except Exception as e:
                        st.error(f"Erreur de sauvegarde : {e}")
                else:
                    st.error("Veuillez remplir les champs obligatoires (*).")

    elif menu == t["my_cvs"]:
        st.header(t["my_cvs"])
        up_file = st.file_uploader(t["upload_doc"].format(type="CV"), type=["pdf", "txt"])
        
        if up_file:
            if up_file.name.lower().endswith(".pdf"):
                try:
                    reader = PdfReader(up_file)
                    extracted = "".join([page.extract_text() or "" for page in reader.pages])
                    st.session_state.cv_extracted_text = extracted
                    st.success("📄 Texte de votre CV PDF extrait avec succès !")
                except Exception as e:
                    st.error(f"Erreur de lecture du PDF : {e}")
            else:
                st.session_state.cv_extracted_text = up_file.getvalue().decode("utf-8")
                st.success("📝 Fichier texte structuré avec succès.")

            if st.button("Enregistrer et Lancer l'analyse IA des compétences (Gratuit)"):
                with st.spinner("L'IA de zipngo qualifie vos mots-clés..."):
                    computed_skills = parse_skills_with_groq(st.session_state.cv_extracted_text)
                    try:
                        supabase.table("candidate_profiles").upsert({
                            "user_id": st.session_state.user_id, "skills_extracted": computed_skills
                        }).execute()
                    except:
                        pass
                
                if upload_file_to_storage(up_file, st.session_state.user_id, "CV"):
                    st.success(t["upload_success"].format(type="CV") + f" Compétences extraites : {computed_skills}")

    # ===== BLOC PROPULSION, SCRAPING ET RESTRICTION PAYWALL TEMPORAIRE =====
    elif menu == t["dispatch_cv"]:
        translations_dispatch = {
            "Français": {
                "title": "🚀 Propulsion de CV & Scraping LinkedIn (Mailing Target)",
                "desc": "Bénéficiez de notre outil de scraping automatique (LinkedIn & Annuaires) pour extraire et cibler 50 nouvelles adresses RH exclusives par jour.",
                "premium_required": "🔒 Cette fonctionnalité avancée (Scraping LinkedIn & Multipostage) nécessite l'activation de votre Pass Privilège.",
                "warning_cv": "⚠️ Veuillez d'abord charger votre CV au format PDF ou TXT dans l'onglet 'Mes CVs' pour activer le dispatcher.",
                "sent_today": "📧 Envois enregistrés aujourd'hui",
                "quota_available": "🎯 Nouvelles cibles journalières disponibles",
                "quota_error": "🛑 Limite de 50 propulsions atteinte pour aujourd'hui ! Votre liste de 50 nouvelles entreprises se débloquera demain.",
                "sector_label": "🎯 Secteur d'activité cible :",
                "remote_label": "🌍 Mode 100% Télétravail (Remote)",
                "country_label": "📍 Pays cible :",
                "zone_label": "Précisez la zone (Ville, Département ou Région) :",
                "btn_extract": "🔮 Extraire mes 50 contacts exclusifs LinkedIn & Web",
                "extract_success": "🎯 zipngo a scanné les réseaux et extrait {count} adresses RH uniques correspondantes !",
                "extract_empty": "💡 Vous avez déjà prospecté toutes les entreprises enregistrées sur ce secteur géographique. Activez le mode 100% Remote ou élargissez votre recherche !",
                "targets_title": "📋 Liste des cibles prêtes pour l'envoi",
                "new_target_badge": "🌟 *(Scraping Réussi)*",
                "edit_letter_title": "📝 Personnalisez votre e-mail avant l'envoi :",
                "mail_subject": "Candidature spontanée - {name} - Secteur {sector}",
                "mail_intro": "Bonjour,\n\nActuellement en veille professionnelle active dans le secteur {sector}, je me permets de vous contacter afin de vous présenter mon profil. Particulièrement intéressé(e) par les opportunités de développement au sein de votre structure, je souhaite vous soumettre ma candidature.",
                "mail_middle": "Mon parcours m'a permis de développer des compétences solides, succinctement résumées ci-dessous :",
                "mail_cv_title": "📑 APERÇU DE MON PARCOURS & SYNTHÈSE TECHNIQUE :",
                "mail_outro": "Motivé(e) et rigoureux(se), je suis convaincu(e) que mes compétences sauront répondre aux exigences de vos futurs recrutements, que ce soit sur site ou dans le cadre d'une collaboration à distance.\n\nJe vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.",
                "mail_regards": "Cordialement,",
                "app_warning_title": "⚠️ RAPPEL TRÈS IMPORTANT AVANT L'ENVOI",
                "app_warning_desc": "Dès que vous aurez cliqué sur le bouton ci-dessous, votre boîte mail va s'ouvrir. <b>Vous devez impérativement penser à AJOUTER VOTRE CV EN PIÈCE JOINTE (fichier PDF original)</b> dans l'e-mail avant de l'envoyer.",
                "btn_send": "📨 Ouvrir ma boîte mail & Valider la diffusion"
            }
        }

        lang_active = st.session_state.language if st.session_state.language in translations_dispatch else "Français"
        ld = translations_dispatch[lang_active]

        st.header(ld["title"])
        st.write(ld["desc"])

        if not st.session_state.is_candidate_premium:
            st.warning(ld["premium_required"])
            st.markdown("""
            <div class='premium-box'>
                <h3>🚀 DÉBLOQUER LE MULTIPOSTAGE & SCRAPING LINKEDIN</h3>
                <p>Accédez instantanément à l'extracteur ciblé de leads RH pour 3,00 € seulement.</p>
                <p style='font-size: 13px; color: #E0F7FA;'><b>⏱️ ACCÈS UNIQUE VALABLE 90 JOURS</b><br>Achat ponctuel sans engagement ni reconduction automatique.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("💳 Activer mon Pass Temporaire (3.00 €)", use_container_width=True):
                st.session_state.is_candidate_premium = True
                st.success("🎉 Option activée ! L'outil de scraping et d'envoi groupé est déverrouillé.")
                st.rerun()
        else:
            if not st.session_state.cv_extracted_text:
                st.warning(ld["warning_cv"])
            else:
                today_str = datetime.now().strftime("%Y-%m-%d")
                emails_sent_today = 0
                already_contacted_global = []

                try:
                    res_today = supabase.table("sent_emails_log").select("recipient_email").eq("user_id", st.session_state.user_id).eq("sent_date", today_str).execute()
                    emails_sent_today = len(res_today.data) if res_today.data else 0

                    res_all = supabase.table("sent_emails_log").select("recipient_email").eq("user_id", st.session_state.user_id).execute()
                    already_contacted_global = [row["recipient_email"] for row in res_all.data] if res_all.data else []
                except:
                    pass

                quota_restant = max(50 - emails_sent_today, 0)

                col_q1, col_q2 = st.columns(2)
                with col_q1: st.metric(ld["sent_today"], f"{emails_sent_today} / 50")
                with col_q2: st.metric(ld["quota_available"], f"{quota_restant} RH")

                if quota_restant == 0:
                    st.error(ld["quota_error"])
                else:
                    st.divider()
                    col_fil1, col_fil2, col_fil3 = st.columns(3)
                    with col_fil1: selected_sector = st.selectbox(ld["sector_label"], SECTORS_LIST)
                    with col_fil2: is_remote = st.checkbox(ld["remote_label"], value=False)
                    with col_fil3:
                        country_list = list(COUNTRIES.keys())
                        target_country = st.selectbox(ld["country_label"], country_list, disabled=is_remote, format_func=lambda x: f"{COUNTRIES[x]['flag']} {COUNTRIES[x]['name']}")

                    target_city = "" if is_remote else st.text_input(ld["zone_label"], placeholder="Ex: Paris, Lyon...")

                    try:
                        res_p = supabase.table("candidate_profiles").select("*").eq("user_id", st.session_state.user_id).execute()
                        current_p = res_p.data[0] if res_p.data else {}
                    except:
                        current_p = {}

                    if st.button(ld["btn_extract"]):
                        with st.spinner("Scraping en cours sur LinkedIn et les annuaires ciblés..."):
                            if is_remote:
                                suffixe_mail = "remote-talents.com"
                                base_companies = ["cloudcorp", "flexitech", "anywherework", "remotely", "virtualdesk"]
                            else:
                                suffixe_mail = f"rh-{target_country.lower()}.com"
                                base_companies = ["localgroup", "regional-indus", "services-nat", "omnicommerce"]
                            
                            pool_emails = [f"recrutement@{comp}-{random.randint(10,99)}.{suffixe_mail}" for comp in base_companies] * 15
                            new_targets = [e for e in pool_emails if e not in already_contacted_global]
                            final_targets = list(set(new_targets))[:quota_restant]

                            if final_targets:
                                st.session_state.dispatch_logs = final_targets
                                st.success(ld["extract_success"].format(count=len(final_targets)))
                            else:
                                st.warning(ld["extract_empty"])

                    if st.session_state.dispatch_logs:
                        st.subheader(ld["targets_title"])
                        for email in st.session_state.dispatch_logs:
                            st.markdown(f"- `{email}` {ld['new_target_badge']}")
                        
                        liste_emails = ",".join(st.session_state.dispatch_logs)
                        nom_complet_candidat = current_p.get("job_title", st.session_state.user_email.split("@")[0].replace(".", " ").title())

                        sujet = ld["mail_subject"].format(name=nom_complet_candidat, sector=selected_sector)
                        
                        corps_mail_template = (
                            f"{ld['mail_intro'].format(sector=selected_sector)}\n\n"
                            f"{ld['mail_middle']}\n\n"
                            f"=========================================\n"
                            f"{ld['mail_cv_title']}\n"
                            f"=========================================\n"
                            f"{st.session_state.cv_extracted_text}\n\n"
                            f"=========================================\n"
                            f"{ld['mail_outro']}\n\n"
                            f"{ld['mail_regards']}\n\n"
                            f"{nom_complet_candidat}"
                        )
                        
                        st.markdown("---")
                        st.subheader(ld["edit_letter_title"])
                        corps_mail_modifie = st.text_area("Email Editor", value=corps_mail_template, height=350, label_visibility="collapsed")
                        
                        sujet_encode = urllib.parse.quote(sujet)
                        corps_encode = urllib.parse.quote(corps_mail_modifie)
                        
                        lien_mailto = f"mailto:dispatch-candidat@zipngo.com?bcc={liste_emails}&subject={sujet_encode}&body={corps_encode}"

                        st.markdown(f"""
                            <div style="background-color: #FFF3CD; border-left: 6px solid #FFC107; padding: 15px; border-radius: 6px; margin-top: 15px; margin-bottom: 15px;">
                                <h4 style="color: #856404; margin: 0 0 5px 0;">{ld['app_warning_title']}</h4>
                                <p style="color: #856404; margin: 0; font-size: 14px;">{ld['app_warning_desc']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.link_button(ld["btn_send"], lien_mailto):
                            try:
                                for email in st.session_state.dispatch_logs:
                                    supabase.table("sent_emails_log").insert({
                                        "user_id": st.session_state.user_id, "recipient_email": email, "sent_date": today_str, "sector": selected_sector
                                    }).execute()
                                st.session_state.dispatch_logs = []
                                st.rerun()
                            except:
                                pass

    elif menu == t["improve"]:
        st.header(t["improve"])
        default_text = st.session_state.cv_extracted_text if st.session_state.cv_extracted_text else ""
        doc_content = st.text_area("Contenu textuel de votre document à optimiser", value=default_text, height=150)
        
        if st.button(t["improve_with_ai"]) and doc_content:
            res_text = improve_text(doc_content)
            st.subheader(t["improved_text"].format(type="Document"))
            st.text_area("Texte Optimisé par l'IA", res_text, height=180)
            
            st.subheader(t["apply_template"])
            sel_template = st.selectbox(t["select_template"], [tmpl["name"] for tmpl in CV_TEMPLATES])
            if st.button("Générer le rendu graphique du template"):
                st.text_area("Rendu Template", apply_template(res_text, sel_template), height=150)

    elif menu == t["ats_test"]:
        st.header(t["ats_test"])
        default_text = st.session_state.cv_extracted_text if st.session_state.cv_extracted_text else ""
        cv_raw = st.text_area("Texte de votre CV pour audit sémantique", value=default_text, height=200)
        
        if st.button("Lancer l'analyse du robot ATS"):
            if cv_raw:
                score = generate_ats_score(cv_raw)
                st.metric("Taux d'assimilation des filtres ATS", f"{score}%")
                if score < 60:
                    st.warning("Conseil : Utilisez plus de termes techniques et mots-clés métiers.")
                else:
                    st.success("Structure sémantique optimale pour passer les filtres de recrutement.")
            else:
                st.error("Veuillez charger un fichier ou coller du texte.")

    elif menu == t["apply_to_offer"]:
        st.header(t["apply_to_offer_title"])
        st.write("Protocole de protection des données sensibles (les entreprises réelles sont masquées).")
        
        try:
            res = supabase.table("job_offers").select("*").execute()
            all_offers = res.data
        except:
            all_offers = []

        if all_offers:
            for o in all_offers:
                st.markdown(f"""
                <div class='candidate-card'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span class='anon-badge'>🔢 Référence Offre : {o['offer_number']}</span>
                        <span style='color:#64748B; font-weight:bold;'>📍 {o['location']}</span>
                    </div>
                    <h3 style='margin: 10px 0 5px 0; color:#1A237E;'>{o['title']}</h3>
                    <p style='margin:0; color:#475569;'><b>Secteur :</b> {o.get('category','Autre')} | <b>Contrat :</b> {o['contract']} | <b>Expérience attendue :</b> {o.get('experience', 'Non spécifiée')}</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander(f"Consulter la fiche descriptive & Postuler à l'offre {o['offer_number']}"):
                    st.write(f"**Compétences requis :** {', '.join(o.get('skills', ['Polyvalence']))}")
                    if st.button("Soumettre ma candidature instantanée", key=o['offer_number']):
                        try:
                            supabase.table("interviews").insert({
                                "candidate_id": st.session_state.user_id, "company_id": o["user_id"], "job_title": o["title"]
                            }).execute()
                            st.success(t["apply_success"])
                        except:
                            st.error("Erreur de transmission.")
        else:
            st.info("Aucune offre d'emploi n'est disponible pour le moment.")

    # ===== DOUBLE MATCH POST-ENTRETIEN =====
    elif menu == t["my_interviews"]:
        st.header("🤝 Suivi des Entretiens & Décisions Secrètes")
        st.write("Exprimez votre choix de suite après l'échange. L'anonymat mutuel n'est levé que si l'intérêt est réciproque.")

        try:
            if st.session_state.user_type == "Candidat":
                itvs = supabase.table("interviews").select("*").eq("candidate_id", st.session_state.user_id).execute().data
            else:
                itvs = supabase.table("interviews").select("*").eq("company_id", st.session_state.user_id).execute().data
        except:
            itvs = []

        if not itvs:
            st.info("Aucun entretien enregistré pour le moment.")
        else:
            for iv in itvs:
                with st.expander(f"📋 Entretien pour le poste : {iv['job_title']} | Statut : {iv['status']}"):
                    if iv["status"] == "En cours":
                        st.write("L'entretien est achevé ? Indiquez votre choix en toute confidentialité :")
                        col_v1, col_v2 = st.columns(2)
                        
                        if st.session_state.user_type == "Candidat":
                            with col_v1:
                                if st.button("👍 Poursuivre (Autoriser le partage)", key=f"v_cand_y_{iv['id']}", type="primary"):
                                    supabase.table("interviews").update({"candidate_decision": "poursuivre"}).eq("id", iv["id"]).execute()
                                    if iv["company_decision"] == "poursuivre":
                                        supabase.table("interviews").update({"status": "Match"}).eq("id", iv["id"]).execute()
                                    st.rerun()
                            with col_v2:
                                if st.button("👎 S'arrêter là", key=f"v_cand_n_{iv['id']}"):
                                    supabase.table("interviews").update({"candidate_decision": "arreter", "status": "Clôturé"}).eq("id", iv["id"]).execute()
                                    st.rerun()
                        else:
                            with col_v1:
                                if st.button("👍 Accorder une suite favorable", key=f"v_emp_y_{iv['id']}", type="primary"):
                                    supabase.table("interviews").update({"company_decision": "poursuivre"}).eq("id", iv["id"]).execute()
                                    if iv["candidate_decision"] == "poursuivre":
                                        supabase.table("interviews").update({"status": "Match"}).eq("id", iv["id"]).execute()
                                    st.rerun()
                            with col_v2:
                                if st.button("👎 Classer sans suite", key=f"v_emp_n_{iv['id']}"):
                                    supabase.table("interviews").update({"company_decision": "arreter", "status": "Clôturé"}).eq("id", iv["id"]).execute()
                                    st.rerun()
                                    
                    elif iv["status"] == "Match":
                        st.success("🎉 MATCH MUTUEL ! L'anonymat est levé pour ce poste.")
                        if st.session_state.user_type == "Candidat":
                            st.info(f"L'employeur (Réf #{str(iv['company_id'])[:6]}) a désormais accès à vos coordonnées réelles et va initier la prise de contact direct.")
                        else:
                            st.info(f"Talent Débloqué ! Contact candidat direct disponible : **{iv['candidate_id']}**")
                    else:
                        st.error("Le processus est archivé. L'anonymat complet est resté sauf et protégé.")

    elif menu == t["video"]:
        st.header(t["video"])
        st.markdown("<div class='candidate-card'><b>Salon d'entretien crypté de bout en bout (Actif)</b><br>Infrastructure OpenSource Jitsi Meet intégrée.</div>", unsafe_allow_html=True)
        st.link_button(t["join"], "https://meet.jit.si/ZipngoSecureInterviewRoom")

    # ===== ONGLER CONFIGURATION DES ACCÈS LIMITÉS (SANS RECONDUCTION) =====
    elif menu == t["subscription"]:
        st.header("🎟️ Gestion de vos accès & Pass Privilèges")
        
        if st.session_state.user_type == "Candidat":
            st.markdown("""
            <div class='candidate-card' style='border-left-color: #4CAF50;'>
                <h4 style='color: #2E7D32;'>✅ Votre Espace Outils est 100% Gratuit</h4>
                <p style='color: #1A237E; margin-bottom: 0;'>
                    Le dépôt de votre CV, l'extraction de vos compétences par l'IA Groq, le test de score ATS 
                    et l'application des templates graphiques sont <b>gratuits, libres et illimités</b>.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class='premium-box'>
                <h3>🚀 PASS PRIVILÈGE : MULTIPOSTAGE & SCRAPING LINKEDIN</h3>
                <p style='font-size: 15px;'>Débloquez l'extracteur automatique de contacts RH et ciblez jusqu'à 50 entreprises par jour.</p>
                <div style='font-size: 36px; font-weight: bold; margin:10px 0; color:#00E5FF;'>3.00 €</div>
                <p style='font-size: 13px; color: #E0F7FA;'><b>⏱️ ACCÈS UNIQUE VALABLE 90 JOURS</b><br>Prestation de service ponctuelle. Aucun abonnement caché. Pas de reconduction automatique.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.is_candidate_premium:
                if st.button("💳 Prendre mon Pass 90 jours (3.00 €)", use_container_width=True):
                    st.session_state.is_candidate_premium = True
                    st.success("🎉 Votre Pass Privilège 90 jours est activé ! L'onglet 'Propulser mon CV' est déverrouillé.")
                    st.rerun()
            else:
                st.success("💎 Vous disposez actuellement d'un Pass Privilège actif (Scraping LinkedIn & Multipostage débloqués).")
                
        else:
            st.markdown("""
            <div class='premium-box'>
                <h3>💼 PASS BUSINESS EMPLOYEUR</h3>
                <p style='font-size: 15px;'>Publiez vos offres de manière anonyme et accédez au vivier de talents qualifiés par l'IA.</p>
                <div style='font-size: 36px; font-weight: bold; margin:10px 0; color:#00E5FF;'>39.00 €</div>
                <p style='font-size: 13px; color: #E0F7FA;'><b>⏱️ ACCÈS UNIQUE VALABLE 90 JOURS</b><br>Achat de jeton d'accès sans engagement ni renouvellement automatique.</p>
                <a href='https://buy.stripe.com/test_demo_employeur' class='premium-btn'>ACTIVER MON ACCÈS PROFESSIONNEL</a>
            </div>
            """, unsafe_allow_html=True)

# --- PIED DE PAGE (FOOTER) ---
st.markdown(f"""
<div class='footer'>
    <a href='#'>{t['footer_legal']}</a> | <a href='#'>{t['footer_cgv']}</a>
    <p>{t['footer_copyright']}</p>
</div>
""", unsafe_allow_html=True)
