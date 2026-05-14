import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="neoCRM.zaxx | Commando", layout="wide")

LANGUAGES = ["Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", "Português", "Русский", "中文", "日本語", "한국어", "العربية", "हिन्दी", "Türkçe", "Nederlands", "Polski", "Svenska", "Tiếng Việt", "Ελληνικά", "Português (BR)"]

# --- STYLE & DESIGN ---
def apply_neo_ui():
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #1A237E !important; border-right: 3px solid #00E5FF; }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }
        .stButton>button { background: #00E5FF !important; color: #1A237E !important; font-weight: 700; border-radius: 8px; width: 100%; border: none; }
        .footer { position: fixed; left: 0; bottom: 0; width: 100%; background: white; text-align: center; padding: 10px; font-size: 11px; border-top: 1px solid #E2E8F0; z-index: 999; }
        .footer a { color: #00E5FF; text-decoration: none; margin: 0 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def display_footer():
    st.markdown("""<div class="footer">© 2026 <b>neocrm.zaxx</b> | Propriété de ZAXX Group | Direction : Liliane RAKOTOBE <br>
    <a href="#">CGV</a> | <a href="#">Mentions Légales</a> | <a href="#">Confidentialité</a> | <a href="#">Support</a></div>""", unsafe_allow_html=True)

# --- ÉTAT ---
if "auth" not in st.session_state: st.session_state.auth = False
if "view" not in st.session_state: st.session_state.view = "login"
if "email" not in st.session_state: st.session_state.email = "contact@neocrm.app"

apply_neo_ui()

# --- VUE : AUTH ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>neo<span style='color:#00E5FF;'>CRM</span>.zaxx</h1>", unsafe_allow_html=True)
        if st.session_state.view == "login":
            with st.container(border=True):
                st.text_input("Identifiant", value=st.session_state.email)
                st.text_input("Mot de passe", type="password")
                st.selectbox("Langue", LANGUAGES)
                role = st.selectbox("Grade", ["teleprospecteur", "expert", "manager", "supermanager"])
                if st.button("ACCÉDER AU SYSTÈME"):
                    st.session_state.auth = True
                    st.session_state.role = role
                    st.rerun()
                st.button("Mot de passe oublié ?", on_click=lambda: st.session_state.update({"view": "forgot"}))
        elif st.session_state.view == "forgot":
            with st.container(border=True):
                st.subheader("Récupération")
                st.text_input("Email")
                if st.button("Envoyer le lien"): st.success("Lien envoyé !")
                st.button("Retour", on_click=lambda: st.session_state.update({"view": "login"}))
    display_footer()
else:
    # Contenu Dashboard (Menu, Commissions, etc.)
    with st.sidebar:
        st.title("neoCRM.zaxx")
        menu = st.radio("Menu", ["📊 Dashboard", "⚡ Commissions", "⚙️ Profil"])
        if st.button("Quitter"): st.session_state.auth = False; st.rerun()
    st.header(f"Bienvenue sur neoCRM - {menu}")
    display_footer()
