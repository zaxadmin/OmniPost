import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="neocrm.zaxx | Supabase Enterprise Ecosystem", layout="wide")

# --- INITIALISATION SUPABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("⚠️ Erreur de configuration Supabase. Veuillez vérifier vos 'Secrets' Streamlit.")
    st.stop()

# --- SYSTÈME DE LANGUES TRADUITES (20 LANGUES COMPLETES ET CORRIGÉES) ---
LANG_MAP = {
    "Français": "fr", "English (US)": "en", "Malgache": "mg", "Español": "es", 
    "Deutsch": "de", "Italiano": "it", "Português": "pt", "Nederlands": "nl",
    "Русский": "ru", "日本語": "ja", "한국어": "ko", "中文": "zh",
    "العربية": "ar", "हिन्दी": "hi", "Türkçe": "tr", "Polski": "pl",
    "Svenska": "sv", "Tiếng Việt": "vi", "ไทย": "th", "Ελληνικά": "el"
}

TEXTS = {
    "Français": {
        "intro": "L'écosystème CRM de pointe pour propulser vos ventes.",
        "desc": "neocrm.zaxx est la solution que nous avons conçue pour centraliser l'intelligence commerciale, optimiser vos conversions et collaborer en temps réel.",
        "uid": "Identifiant de connexion / Adresse Email", "pwd": "Mot de passe",
        "btn_login": "ACCÉDER À MON CRM / ACTIVATION", "btn_lost": "mots de passe perdu", "btn_create": "CREER UN COMPTE"
    },
    "English (US)": {
        "intro": "The cutting-edge CRM ecosystem to boost your sales.",
        "desc": "neocrm.zaxx is the solution we designed to centralize commercial intelligence, optimize conversions, and collaborate in real-time.",
        "uid": "Login ID / Email Address", "pwd": "Password",
        "btn_login": "ACCESS MY CRM / ACTIVATION", "btn_lost": "lost password", "btn_create": "CREATE AN ACCOUNT"
    },
    "Malgache": {
        "intro": "Ny rafitra CRM farany indrindra hampitomboana ny fivarotanao.",
        "desc": "neocrm.zaxx dia vahaolana namboarinay hanambarana ny fahaiza-manao ara-barotra sy hiaraha-miasa amin'ny fotoana tena izy.",
        "uid": "Anarana fidirana / Mailaka", "pwd": "Teny miafina",
        "btn_login": "HIDITRA AMIN'NY CRM / ACTIVATION", "btn_lost": "hadino ny teny miafina", "btn_create": "HANOKATRA KAONTY"
    },
    "Español": {
        "intro": "El ecosistema CRM de vanguardia para impulsar sus ventas.",
        "desc": "neocrm.zaxx is la solución diseñada para centralizar la intelligence comercial, optimizar conversiones y colaborar en tiempo real.",
        "uid": "Identificación de ingreso / Correo electrónico", "pwd": "Contraseña",
        "btn_login": "ACCEDER A MI CRM / ACTIVACIÓN", "btn_lost": "contraseña perdida", "btn_create": "CREAR UNA CUENTA"
    },
    "Deutsch": {
        "intro": "Das führende CRM-Ökosystem zur Steigerung Ihres Umsatzes.",
        "desc": "neocrm.zaxx ist die Lösung, die wir entwickelt haben, um Vertriebsintelligenz zu zentralisieren, Conversions zu optimieren und in Echtzeit zusammenzuarbeiten.",
