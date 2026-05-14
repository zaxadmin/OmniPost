import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Flux Logistique", layout="wide")

LANGUAGES = [
    "Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", 
    "Português", "Русский", "中文", "日本語", "한국어", "العربية", "हिन्दी", 
    "Türkçe", "Nederlands", "Polski", "Svenska", "Tiếng Việt", "Ελληνικά", "Português (BR)"
]

# --- DESIGN & FOOTER ---
def apply_zip_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 2px solid #00E5FF; }
        .stButton>button { 
            background: #1A237E !important; color: #00E5FF !important; 
            border-radius: 25px; border: 2px solid #00E5FF; font-weight: bold; width: 100%;
        }
        .footer-zip { 
            position: fixed; left: 0; bottom: 0; width: 100%; 
            background: #1A237E; color: white; text-align: center; 
            padding: 15px; font-size: 11px; z-index: 999; 
        }
        .footer-zip a { color: #00E5FF; text-decoration: none; margin: 0 15px; font-weight: bold; }
        .flux-card { background: #F8FAFC; padding: 20px; border-radius: 12px; border-left: 10px solid #1A237E; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def display_footer_zip():
    st.markdown("""<div class="footer-zip"><b>zipngo.zaxx</b> - Opérations & Closing | © 2026 ZAXX Group <br>
    <a href="#">CGV</a> | <a href="#">PROTECTION DES DONNÉES</a> | <a href="#">CONTACT LILIANE RAKOTOBE</a></div>""", unsafe_allow_html=True)

# --- ÉTAT ---
if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"
if "z_mail" not in st.session_state: st.session_state.z_mail = "admin@zipngo.app"

apply_zip_theme()

# --- VUE : ACCÈS ET INSCRIPTION ---
if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        # Titre avec .zaxx obligatoire
        st.markdown("<h1 style='text-align:center; font-size: 50px;'>zip<span style='color:#00E5FF;'>ngo</span><span style='font-size:20px; font-weight:300;'>.zaxx</span></h1>", unsafe_allow_html=True)
        
        mode = st.radio("Accès au Flux", ["Connexion", "S'inscrire"], horizontal=True)
        
        if mode == "Connexion":
            if st.session_state.z_view == "login":
                with st.container(border=True):
                    st.text_input("Identifiant zipngo", value=st.session_state.z_mail, key="z_l")
                    st.text_input("Clé d'accès", type="password", key="z_p")
                    st.selectbox("Language / Langue", LANGUAGES)
                    if st.button("LANCER LA SESSION"):
                        st.session_state.z_auth = True
                        st.rerun()
                    st.button("Mot de passe oublié ?", on_click=lambda: st.session_state.update({"z_view": "forgot"}))
            elif st.session_state.z_view == "forgot":
                st.subheader("Récupération")
                st.text_input("Email enregistré")
                if st.button("Récupérer clé"): st.info("Instructions de sécurité envoyées.")
                st.button("Retour", on_click=lambda: st.session_state.update({"z_view": "login"}))
        else:
            with st.container(border=True):
                st.subheader("Créer un compte Flux")
                st.text_input("Entité / Nom complet")
                st.text_input("Email d'accès")
                st.text_input("Mot de passe souhaité", type="password")
                st.selectbox("Zone Opérationnelle", ["Europe", "Madagascar", "Asie"])
                if st.button("DEMANDER L'ADHÉSION"):
                    st.success("Demande enregistrée. Activation par ZAXX Group imminente.")
    display_footer_zip()

# --- VUE : DASHBOARD ---
else:
    with st.sidebar:
        st.title("zipngo.zaxx")
        menu = st.selectbox("Modules", ["📦 Flux Logistique", "💰 Finance Commando", "⚙️ Mon Compte"])
        if st.button("Déconnexion"):
            st.session_state.z_auth = False
            st.rerun()

    if menu == "📦 Flux Logistique":
        st.header("Gestion des Expéditions")
        st.markdown('<div class="flux-card">🚚 <b>Avis :</b> 14 colis en attente de validation (Madagascar).</div>', unsafe_allow_html=True)
        st.progress(65, text="Objectif de livraison mensuel")
        st.table(pd.DataFrame({'Colis': ['#ZA-01', '#ZA-02'], 'Destination': ['Paris', 'Antananarivo'], 'Statut': ['En route', 'Dédouanement']}))

    elif menu == "💰 Finance Commando":
        st.header("Rémunération")
        ca = st.number_input("CA Closing généré (€)", min_value=0)
        st.metric("Commission SuperManager (35%)", f"{ca * 0.35:,.2f} €")
        
        # Graphique
        hist = pd.DataFrame({'Mois': ['Mars', 'Avril', 'Mai'], 'Gains': [1200, 3100, 2800]})
        st.line_chart(hist.set_index('Mois'))

    elif menu == "⚙️ Mon Compte":
        st.header("Profil")
        st.session_state.z_mail = st.text_input("Email de connexion", value=st.session_state.z_mail)
        st.button("Mettre à jour")

    display_footer_zip()
