import streamlit as st
import PyPDF2
from fpdf import FPDF
from datetime import date, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f2f6 0%, #ffffff 100%); }
    .brand-title { font-size: 3rem; font-weight: 800; text-align: center; }
    .zip { color: #000080; } .ngo { color: #00FFFF; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({
        "auth": False, "profile_completed": False, "premium": False, 
        "alertes": [], "date_inscription": date.today()
    })

def ajouter_alerte(msg):
    if msg not in st.session_state.alertes: st.session_state.alertes.append(msg)

def get_jours_restants():
    delta = (st.session_state.date_inscription + timedelta(days=15 if st.session_state.user_type == "Employeur" else 90)) - date.today()
    return delta.days

# --- AUTHENTIFICATION ---
if not st.session_state.auth:
    col_lang, col_rest = st.columns([1, 4])
    with col_lang:
        st.selectbox("🌐", ["Français", "English", "Español"], label_visibility="collapsed")
    
    st.markdown("<div class='brand-title'><span class='zip'>zip</span><span class='ngo'>ngo</span> 👍</div>", unsafe_allow_html=True)
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"):
        st.session_state.update({"auth": True, "user_type": role})
        st.rerun()

# --- APPLICATION ---
else:
    t = {"dash": "Tableau de bord", "label": "Analyse Profil", "search": "Recherche Talents", "match": "Entretiens", "acc": "Mon Compte"}
    with st.sidebar:
        st.markdown(f"**Statut :** <span style='color:green'>●</span> En ligne", unsafe_allow_html=True)
        st.write(f"⏳ Essai : {get_jours_restants()} jours restants")
        
        # Gestion Premium
        if st.checkbox("Activer Premium"): st.session_state.premium = True
        
        # Alertes
        if st.session_state.alertes:
            st.markdown("### 🔔 Notifications")
            for alerte in st.session_state.alertes: st.info(alerte)
            if st.button("Effacer"): st.session_state.alertes = []
        
        menu = st.radio("Navigation", list(t.values()))

    if menu == t["dash"]:
        st.header("Tableau de bord")
        if get_jours_restants() <= 0 and not st.session_state.premium:
            st.error("Période d'essai terminée. Passez Premium pour continuer.")

    elif menu == t["search"]:
        st.header("Recherche Talents")
        if not st.session_state.premium:
            st.warning("⚠️ Mode Essai : Dispatch géographique et Mode Remote limités.")
            limite = 20
        else:
            st.success("🌟 Accès Premium : Dispatch illimité.")
            limite = 1000
        
        if st.button(f"🔍 Lancer Recherche (Limite : {limite})"):
            st.write([f"Profil {i}" for i in range(1, limite + 1)])

    elif menu == t["match"]:
        st.header("Gestion des Entretiens")
        if st.session_state.user_type == "Employeur":
            if st.button("Proposer RDV"): 
                st.session_state.proposition = True
                ajouter_alerte("Proposition envoyée.")
        else:
            if st.session_state.get("proposition"):
                if st.button("✅ Accepter"): ajouter_alerte("RDV confirmé !")
                if st.button("🔄 Proposer autre heure"): ajouter_alerte("Contre-proposition envoyée.")

    elif menu == t["acc"]:
        st.header("Mon Compte")
        st.info("Votre mode d'emploi est disponible ici.")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
