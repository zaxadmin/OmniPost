import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Flux Logistique", layout="wide")

LANGUAGES = ["Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", "Português", "Русский", "中文", "日本語", "한국어", "العربية", "हिन्दी", "Türkçe", "Nederlands", "Polski", "Svenska", "Tiếng Việt", "Ελληνικά", "Português (BR)"]

# --- STYLE & DESIGN ---
def apply_zip_ui():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 2px solid #00E5FF; }
        .stButton>button { background: #1A237E !important; color: #00E5FF !important; border-radius: 25px; border: 2px solid #00E5FF; font-weight: bold; width: 100%; }
        .footer-zip { position: fixed; left: 0; bottom: 0; width: 100%; background: #1A237E; color: white; text-align: center; padding: 15px; font-size: 11px; z-index: 999; }
        .footer-zip a { color: #00E5FF; text-decoration: none; margin: 0 15px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def display_footer_zip():
    st.markdown("""<div class="footer-zip"><b>zipngo.zaxx</b> - Opérations & Logistique | © 2026 ZAXX Group <br>
    <a href="#">CGV</a> | <a href="#">PROTECTION DES DONNÉES</a> | <a href="#">SUPPORT LILIANE</a></div>""", unsafe_allow_html=True)

# --- ÉTAT ---
if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"
if "z_mail" not in st.session_state: st.session_state.z_mail = "admin@zipngo.app"

apply_zip_ui()

# --- VUE : AUTHENTIFICATION ---
if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        # CORRECTION ICI : Ajout de .zaxx dans le titre d'authentification
        st.markdown("<h1 style='text-align:center; font-size: 50px;'>zip<span style='color:#00E5FF;'>ngo</span><span style='font-size:25px; font-weight:300;'>.zaxx</span></h1>", unsafe_allow_html=True)
        
        if st.session_state.z_view == "login":
            with st.container(border=True):
                st.text_input("Compte de connexion", value=st.session_state.z_mail)
                st.text_input("Mot de passe", type="password")
                st.selectbox("Langue / Language", LANGUAGES)
                if st.button("OUVRIR LE FLUX"):
                    st.session_state.z_auth = True
                    st.rerun()
                st.button("Accès perdu ?", on_click=lambda: st.session_state.update({"z_view": "forgot"}))
        
        elif st.session_state.z_view == "forgot":
            with st.container(border=True):
                st.subheader("Réinitialisation")
                st.text_input("Email enregistré")
                if st.button("Récupérer"): st.info("Lien envoyé.")
                st.button("Retour", on_click=lambda: st.session_state.update({"z_view": "login"}))
    display_footer_zip()
else:
    # Contenu Dashboard (Flux, Finance, Paramètres)
    with st.sidebar:
        st.title("zipngo.zaxx")
        menu = st.selectbox("Modules", ["📦 Flux", "💰 Finance", "⚙️ Profil"])
        if st.button("Déconnexion"): st.session_state.z_auth = False; st.rerun()
    
    if menu == "⚙️ Profil":
        st.header("Paramètres")
        st.session_state.z_mail = st.text_input("Changer l'email", value=st.session_state.z_mail)
        if st.button("Sauvegarder"): st.success("Email mis à jour.")
    else:
        st.header(f"Section {menu}")
    
    display_footer_zip()
