import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Flux Logistique", layout="wide")

LANGUAGES = ["Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", "Português", "Русский", "中文", "日本語", "한국어", "العربية", "हिन्दी", "Türkçe", "Nederlands", "Polski", "Svenska", "Tiếng Việt", "Ελληνικά", "Português (BR)"]

# --- DESIGN ET STYLE ---
def apply_zip_ui():
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #F0F4F8 !important; border-right: 3px solid #00E5FF; }
        
        /* Boutons Zipngo (Marine & Cyan) */
        .stButton>button { 
            background: #1A237E !important; color: #00E5FF !important; 
            border-radius: 25px; border: 2px solid #00E5FF; font-weight: bold;
        }

        /* Footer Zipngo */
        .footer-zip {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background-color: #1A237E; color: white; text-align: center;
            padding: 15px; font-size: 11px; z-index: 100;
        }
        .footer-zip a { color: #00E5FF; text-decoration: none; margin: 0 15px; }

        /* Cartes d'information */
        .flux-card { background: #F8FAFC; padding: 20px; border-radius: 12px; border-left: 8px solid #1A237E; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def display_footer_zip():
    st.markdown("""
    <div class="footer-zip">
        <b>zipngo.zaxx</b> - Opérations & Logistique Mondiale | © 2026 ZAXX Group <br>
        <a href="#">CGV</a> | <a href="#">PROTECTION DES DONNÉES</a> | <a href="#">COOKIES</a> | <a href="#">LILIANE RAKOTOBE</a>
    </div>
    """, unsafe_allow_html=True)

# --- ÉTAT SYSTÈME ---
if "zip_auth" not in st.session_state: st.session_state.zip_auth = False
if "zip_view" not in st.session_state: st.session_state.zip_view = "login"
if "zip_mail" not in st.session_state: st.session_state.zip_mail = "admin@zipngo.app"

apply_zip_ui()

# --- VUE : AUTHENTIFICATION ---
if not st.session_state.zip_auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align:center; font-size: 50px;'>zip<span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
        
        if st.session_state.zip_view == "login":
            with st.container(border=True):
                st.text_input("Compte Utilisateur", value=st.session_state.zip_mail)
                st.text_input("Clé d'Accès", type="password")
                st.selectbox("Language", LANGUAGES)
                if st.button("OUVRIR LA SESSION"):
                    st.session_state.zip_auth = True
                    st.rerun()
                st.button("Mot de passe oublié ?", on_click=lambda: st.session_state.update({"zip_view": "forgot"}))
        
        elif st.session_state.zip_view == "forgot":
            with st.container(border=True):
                st.subheader("Réinitialisation zipngo")
                st.text_input("Email de récupération")
                if st.button("Récupérer l'accès"): st.info("Un code temporaire vous a été envoyé.")
                st.button("Retour", on_click=lambda: st.session_state.update({"zip_view": "login"}))
    display_footer_zip()

# --- VUE : LOGISTIQUE & FINANCE ---
else:
    with st.sidebar:
        st.markdown("### zipngo.zaxx")
        menu = st.selectbox("Modules", ["📦 Flux Logistique", "💰 Finance Commando", "⚙️ Mon Compte"])
        if st.button("Terminer la session"):
            st.session_state.zip_auth = False
            st.rerun()

    if menu == "📦 Flux Logistique":
        st.header("Gestion des Expéditions")
        st.markdown('<div class="flux-card">🚚 <b>Avis :</b> 14 colis en attente de dédouanement (Antananarivo).</div>', unsafe_allow_html=True)
        st.progress(65, text="Objectif de livraison global")
        
        # Liste fictive
        flux_data = {"ID Colis": ["#998", "#999", "#1000"], "Destination": ["Paris", "Marseille", "Tamatave"], "État": ["Livré", "Transit", "Préparation"]}
        st.table(pd.DataFrame(flux_data))

    elif menu == "💰 Finance Commando":
        st.header("Rémunération & Reporting")
        vente = st.number_input("Chiffre d'affaires Closing (€)", min_value=0)
        st.metric("Commission SuperManager (35%)", f"{vente * 0.35:,.2f} €")
        
        st.write("### Historique des Gains")
        hist = pd.DataFrame({"Mois": ["Janvier", "Février"], "Gains (€)": [1200, 3450]})
        st.bar_chart(hist.set_index("Mois"))

    elif menu == "⚙️ Mon Compte":
        st.header("Paramètres du Profil")
        st.session_state.zip_mail = st.text_input("Email de connexion", value=st.session_state.zip_mail)
        st.password = st.text_input("Changer le mot de passe", type="password")
        if st.button("Sauvegarder les changements"):
            st.success("Profil mis à jour.")

    display_footer_zip()
