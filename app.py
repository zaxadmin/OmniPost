import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
from supabase import create_client, Client
from pypdf import PdfReader
import requests
import json
import os

# --- CONFIGURATION DE PAGE ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- INITIALISATION DES APIS (SECRETS) ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    GROQ_API_KEY = st.secrets["groq"]["api_key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Erreur de configuration des clés API (Vérifie tes secrets Streamlit) : {e}")
    st.stop()

# --- ROUTINE DE BLACKLIST ---
def traiter_blacklist():
    query_params = st.query_params
    if "blacklist" in query_params:
        email = query_params["email"]
        supabase.table("users").update({"is_blacklisted": True}).eq("user_email", email).execute()
        st.success(f"L'adresse {email} a bien été ajoutée à la liste noire.")
        st.stop()

traiter_blacklist()

# --- NOUVEAUX DIALOGUES (CGV / MENTIONS) ---
@st.dialog("⚖️ Conditions Générales de Vente")
def afficher_cgv(): st.write("Zipngo permet la diffusion locale ou 100% Remote sans frontières. Les conditions sont régies par le contrat propre à chaque employeur.")
@st.dialog("🔒 Mentions Légales")
def afficher_mentions_legales(): st.write("Éditeur : Liliane RAKOTOBE. Contact : contact@zipngo.app")

# --- DICTIONNAIRE DE LANGUES ---
LANGUAGES = {
    "Français": {
        "rules": "Règles du jeu 📜", "profile": "Mon Profil & ATS 👤", "propulsion": "Propulsion CV 🚀",
        "matches": "Matchs & Entretiens 🤝", "archive": "Tiroir d'archivage 🗄️", "account": "Mon Compte ⚙️",
        "create_job": "Créer une offre ✍️", "broadcast": "Diffuser l'offre 📢", "candidates": "Candidats reçus 🔍",
        "role_cand": "Candidat", "role_emp": "Employeur", "welcome": "Connexion ou Inscription Sécurisée",
        "submit_cv_req": "Action obligatoire pour activer votre inscription", "cv_desc": "L'inscription est gratuite pour 3 mois, mais vous devez obligatoirement déposer votre CV pour le matching automatique.",
        "premium_active": "Option Premium active : Optimisations ATS illimitées.", "premium_info": "🎁 Version Gratuite : Il vous reste {} / 5 réfections de CV.",
        "anonymity_alert": "📢 NOTE CONCERNANT L'ANONYMAT SUR LE DISPATCH : L'envoi s'exécutant via votre messagerie personnelle, votre e-mail réel sera visible.",
        "gold_rule_title": "✨ RÈGLE D'OR DE PUBLICATION AUTOMATIQUE :", "gold_rule_desc": "Toute offre enregistrée est immédiatement intégrée au flux interne de l'application.",
        "global_banner": "🌍 Recrutement 100% Remote & Digital sans frontières"
    },
    "English": {
        "rules": "Rules of the game 📜", "profile": "My Profile & ATS 👤", "propulsion": "CV Propulsion 🚀",
        "matches": "Matches & Interviews 🤝", "archive": "Archiving Drawer 🗄️", "account": "My Account ⚙️",
        "create_job": "Create an offer ✍️", "broadcast": "Broadcast offer 📢", "candidates": "Candidates received 🔍",
        "role_cand": "Candidate", "role_emp": "Employer", "welcome": "Secure Login or Registration",
        "submit_cv_req": "Mandatory action to activate registration", "cv_desc": "Registration is free for 3 months, but you must upload your CV for automatic matching.",
        "premium_active": "Premium Option Active: Unlimited ATS optimizations.", "premium_info": "🎁 Free Version: You have {} / 5 CV updates left.",
        "anonymity_alert": "📢 ANONYMITY NOTICE ON DISPATCH: Sending via your personal email means your real address will be visible.",
        "gold_rule_title": "✨ GOLDEN RULE OF AUTOMATIC PUBLICATION:", "gold_rule_desc": "Any registered offer is immediately integrated into the internal application flow.",
        "global_banner": "🌍 100% Remote & Digital Recruitment without borders"
    }
}

for lang in ["Español", "Deutsch", "Italiano", "Português", "Nederlands", "Русский", "中文", "日本語", "العربية", "Polski", "Türkçe", "Swedish", "Hindi", "Korean", "Bengali", "Punjabi", "Javanese", "Vietnamese"]:
    if lang not in LANGUAGES:
        LANGUAGES[lang] = LANGUAGES["English"]

if "lang" not in st.session_state:
    st.session_state.lang = "Français"

# --- BARRE DE SÉLECTION DE LA LANGUE TOUT EN HAUT ---
col_logo, col_lang = st.columns([5, 1])
with col_lang:
    selected_lang = st.selectbox("🌐", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.lang), label_visibility="collapsed")
    st.session_state.lang = selected_lang
    t = LANGUAGES[st.session_state.lang]

# --- FONCTIONS REELLES IA ---
def appeler_groq_ia(prompt: str, system_instruction: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Erreur API ({response.status_code})"
    except:
        return "Erreur de connexion IA."

def calculer_score_matching_ia(cv_text: str, offre_text: str) -> int:
    system_instruction = "Tu es un algorithme RH. Évalue la correspondance entre le CV et l'offre. Réponds UNIQUEMENT par un nombre entier entre 0 et 100."
    resultat = appeler_groq_ia(f"CV:\n{cv_text}\n\nOffre:\n{offre_text}", system_instruction).strip()
    try:
        return int(''.join(filter(str.isdigit, resultat)))
    except:
        return 50

# --- LOGIQUE MISE À JOUR AUTOMATIQUE ENTREPRISES (7 JOURS) ---
def synchroniser_nouvelles_entreprises():
    mises_a_jour_anciennes = supabase.table("app_settings").select("*").eq("key", "last_company_scraping").execute().data
    devoir_scrapar = False
    maintenant = datetime.now()
    if not mises_a_jour_anciennes:
        devoir_scrapar = True
    else:
        derniere_date = datetime.fromisoformat(mises_a_jour_anciennes[0]["value"])
        if maintenant - derniere_date > timedelta(days=7):
            devoir_scrapar = True
    if devoir_scrapar:
        nouveau_timestamp = {"key": "last_company_scraping", "value": maintenant.isoformat()}
        if not mises_a_jour_anciennes:
            supabase.table("app_settings").insert(nouveau_timestamp).execute()
        else:
            supabase.table("app_settings").update(nouveau_timestamp).eq("key", "last_company_scraping").execute()

try:
    synchroniser_nouvelles_entreprises()
except:
    pass

# --- CAPTURE DU LIEN MAGIQUE DANS L'URL ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_type" not in st.session_state: st.session_state.user_type = None
if "user_id" not in st.session_state: st.session_state.user_id = None
if "candidate_data" not in st.session_state: st.session_state.candidate_data = {}

query_params = st.query_params
if "access_token" in query_params or "#access_token" in query_params:
    try:
        session_user = supabase.auth.get_user()
        if session_user and session_user.user:
            user_email = session_user.user.email
            res = supabase.table("users").select("*").eq("user_email", user_email).execute()
            if len(res.data) > 0:
                user_record = res.data[0]
                st.session_state.auth = True
                st.session_state.user_email = user_email
                st.session_state.user_type = user_record["user_type"]
                st.session_state.user_id = user_record["id"]
                st.query_params.clear()
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"Erreur lors de la validation du lien : {e}")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; color: #1A237E; }
    [data-testid="stSidebar"] { background-color: #1A237E !important; border-right: 3px solid #00E5FF; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stButton>button { background: #1A237E !important; color: #FFFFFF !important; border-radius: 8px; font-weight: 700; }
    .gold-rule { background-color: #E6FFFA; border-left: 4px solid #319795; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
    .candidate-card { padding: 15px; background-color: #FFFFFF; border-left: 4px solid #00E5FF; border-radius: 6px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .info-rules { background-color: #EBF8FF; border-left: 4px solid #3182CE; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
    .marketing-box { background: linear-gradient(135deg, #1A237E, #2A36B1); color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .marketing-box h3 { color: #00E5FF !important; margin-top: 0; }
    .marketing-grid { display: flex; justify-content: space-around; gap: 15px; margin-top: 20px; flex-wrap: wrap; }
    .marketing-item { background: rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 8px; font-size: 14px; flex: 1; min-width: 200px; }
    .custom-footer { text-align: center; color: #64748B; padding-top: 30px; font-size: 13px; line-height: 1.8; }
    .custom-footer button { background: none !important; border: none !important; padding: 0 !important; color: #1A237E !important; text-decoration: none; cursor: pointer; font-weight: 600; font-size: 13px; }
    .custom-footer button:hover { color: #00E5FF !important; text-decoration: underline; }
    .global-banner { background: #00E5FF; color: #1A237E; padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- EXECUTION FLUX D'APPLICATION ---
if not st.session_state.auth:
    _, col, _ = st.columns([0.5, 2.0, 0.5])
    with col:
        st.markdown("<h1 style='text-align:center; font-size: 50px; margin-bottom: 5px;'><span style='color:#1A237E;'>zip</span><span style='color:#00E5FF;'>ngo</span> <span style='font-size: 40px;'>👍</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='global-banner'>{t['global_banner']}</div>", unsafe_allow_html=True)
        st.markdown("""<div class='marketing-box'><h3>Le point de rencontre parfait. Zéro perte de temps. Anonymat absolu.</h3><p>Que vous soyez un <b>Candidat</b> ou un <b>Employeur</b>, Zipngo transforme votre manière de recruter.</p></div>""", unsafe_allow_html=True)
        role = st.radio("Connexion en tant que :", [t["role_cand"], t["role_emp"]], horizontal=True)
        email = st.text_input("E-mail :").strip().lower()
        if st.button("🚀 Recevoir mon Lien Magique"):
            if email:
                supabase.auth.signInWithOtp({"email": email})
                st.success("Lien envoyé par e-mail.")
else:
    user_db = supabase.table("users").select("*").eq("id", st.session_state.user_id).execute().data[0]
    with st.sidebar:
        if st.session_state.user_type == "Candidat":
            menu = st.radio("Navigation", [t["rules"], t["profile"], t["propulsion"], t["matches"], t["archive"], t["account"]])
        else:
            menu = st.radio("Navigation", [t["rules"], t["create_job"], t["broadcast"], t["candidates"], t["matches"], t["archive"], t["account"]])
        if st.button("🚪 Déconnexion"): supabase.auth.sign_out(); st.session_state.auth = False; st.rerun()

    # --- SECTION MATCHS ---
    if menu == t["matches"]:
        st.header(t["matches"])
        champ_filtre = "candidat_id" if st.session_state.user_type == "Candidat" else "employeur_id"
        matchs = supabase.table("matches_interviews").select("*").eq(champ_filtre, st.session_state.user_id).execute().data
        for m in matchs:
            is_confirmed = m.get("thumb_candidat") and m.get("thumb_employeur")
            st.subheader(f"💼 {m.get('job_title', 'Poste')}")
            if is_confirmed:
                st.success("🤝 Match Confirmé !")
                st.link_button("🎥 Lancer l'entretien", f"https://meet.jit.si/zipngo-entretien-{m['id']}")
            else:
                mon_pouce = "thumb_candidat" if st.session_state.user_type == "Candidat" else "thumb_employeur"
                if not m.get(mon_pouce):
                    if st.button("👍 Valider mon intérêt", key=f"v_{m['id']}"):
                        supabase.table("matches_interviews").update({mon_pouce: True}).eq("id", m['id']).execute(); st.rerun()
                else: st.write("✅ En attente de l'autre partie.")

    # --- AUTRES MENUS ---
    elif menu == t["account"]:
        st.header(t["account"])
        st.write(f"E-mail : `{st.session_state.user_email}`")

# --- FOOTER ---
st.markdown("<hr>", unsafe_allow_html=True)
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    email_user = st.session_state.get("user_email", "contact@zipngo.app")
    st.markdown(f"""
    <div style='text-align: center; color: #64748B; font-size: 13px;'>
        © 2026 zipngo | App Creator : <b>Liliane RAKOTOBE</b> 
        <a href="mailto:contact@zipngo.app" style="text-decoration:none;">✉️</a><br>
        <a href="/?blacklist=true&email={email_user}" style="color:red; text-decoration:none;">🚫 Se désinscrire (Blacklist)</a>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⚖️ CGV", use_container_width=True): afficher_cgv()
    with c2:
        if st.button("🔒 Mentions", use_container_width=True): afficher_mentions_legales()
