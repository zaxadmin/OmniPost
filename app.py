import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
from supabase import create_client, Client
from pypdf import PdfReader
import requests
import json
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    GROQ_API_KEY = st.secrets["groq"]["api_key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Erreur config : {e}"); st.stop()

# --- 2. LANGUES ---
LANG_KEYS = ["Français", "English"] # Ajoute les autres ici
LANGUAGES = {
    "Français": {
        "rules": "Règles du jeu 📜", "profile": "Mon Profil & ATS 👤", "propulsion": "Propulsion CV 🚀",
        "matches": "Matchs & Entretiens 🤝", "archive": "Tiroir d'archivage 🗄️", "account": "Mon Compte ⚙️",
        "create_job": "Créer une offre ✍️", "broadcast": "Diffuser 📢", "candidates": "Candidats 🔍",
        "role_cand": "Candidat", "role_emp": "Employeur", "welcome": "Connexion"
    },
    "English": {
        "rules": "Rules 📜", "profile": "My Profile 👤", "propulsion": "CV Propulsion 🚀",
        "matches": "Matches & Interviews 🤝", "archive": "Archive 🗄️", "account": "Account ⚙️",
        "create_job": "Create Job ✍️", "broadcast": "Broadcast 📢", "candidates": "Candidates 🔍",
        "role_cand": "Candidate", "role_emp": "Employer", "welcome": "Login"
    }
}
if "lang" not in st.session_state: st.session_state.lang = "Français"
selected_lang = st.sidebar.selectbox("🌐 Langue", list(LANGUAGES.keys()))
t = LANGUAGES[selected_lang]

# --- 3. FONCTIONS UTILITAIRES ---
def synchroniser_nouvelles_entreprises():
    mises_a_jour = supabase.table("app_settings").select("*").eq("key", "last_company_scraping").execute().data
    maintenant = datetime.now()
    if not mises_a_jour or (maintenant - datetime.fromisoformat(mises_a_jour[0]["value"]) > timedelta(days=7)):
        # Logique de scraping ici
        supabase.table("app_settings").upsert({"key": "last_company_scraping", "value": maintenant.isoformat()}).execute()

# --- 4. FLUX AUTH ---
if not st.session_state.get("auth"):
    st.title("zipngo 👍")
    role = st.radio("Rôle", [t["role_cand"], t["role_emp"]])
    email = st.text_input("E-mail")
    if st.button("Connexion"):
        res = supabase.table("users").select("*").eq("user_email", email).execute()
        if res.data:
            st.session_state.update({"auth": True, "user_id": res.data[0]["id"], "user_type": res.data[0]["user_type"], "user_email": email})
            st.rerun()
else:
    user_db = supabase.table("users").select("*").eq("id", st.session_state.user_id).execute().data[0]
    with st.sidebar:
        menu = st.radio("Navigation", list(t.values()))
        if st.button("🚪 Déconnexion"): st.session_state.auth = False; st.rerun()

    # --- LOGIQUE : MATCHS & JITSI ---
    if menu == t["matches"]:
        st.header(t["matches"])
        matchs = supabase.table("matches_interviews").select("*").eq("candidat_id" if user_db["user_type"] == "Candidat" else "employeur_id", st.session_state.user_id).execute().data
        for m in matchs:
            is_confirmed = m.get("thumb_candidat") and m.get("thumb_employeur")
            st.subheader(f"💼 {m.get('job_title', 'Poste')}")
            if is_confirmed:
                st.success("🤝 Match Confirmé")
                st.link_button("🎥 Lancer l'entretien", f"https://meet.jit.si/zipngo-entretien-{m['id']}#config.prejoinPageEnabled=false")
            else:
                mon_pouce = "thumb_candidat" if user_db["user_type"] == "Candidat" else "thumb_employeur"
                if not m.get(mon_pouce):
                    if st.button("👍 Valider mon intérêt", key=f"v_{m['id']}"):
                        supabase.table("matches_interviews").update({mon_pouce: True}).eq("id", m['id']).execute(); st.rerun()
                else: st.write("✅ En attente de l'autre partie.")

    # --- LOGIQUE : DISPATCH EMPLOYEUR ---
    elif menu == t["candidates"]:
        st.header(t["candidates"])
        candidatures = supabase.table("propulsion_history").select("*, users!inner(*)").eq("recipient_email", user_db["user_email"]).execute().data
        for c in candidatures:
            if st.button(f"Accepter {c['users']['user_email']}", key=f"c_{c['id']}"):
                supabase.table("matches_interviews").insert({"candidat_id": c['candidat_id'], "employeur_id": st.session_state.user_id, "job_title": "Candidature"}).execute()
                st.success("Match créé !")

    # --- LOGIQUE : PREMIUM ---
    elif menu == t["account"]:
        st.header(t["account"])
        usage = supabase.table("usage_stats").select("*").eq("user_id", st.session_state.user_id).execute().data
        count = usage[0].get("cv_updates", 0) if usage else 0
        st.write(f"🎁 Réfections restantes : {5 - count} / 5")
        if count >= 5: st.warning("⚠️ Passez Premium pour continuer.")

    # [Autres menus : rules, profile, propulsion, create_job, broadcast, archive]

# --- FOOTER ---
st.markdown("<hr>© 2026 zipngo | Liliane RAKOTOBE", unsafe_allow_html=True)
