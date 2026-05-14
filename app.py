import streamlit as st
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo.zaxx | Recruitment", layout="wide")

# --- STYLE & VISIBILITÉ ---
st.markdown("""
<style>
    label { color: #1A237E !important; font-weight: bold !important; font-size: 1.1rem !important; }
    .stApp { background-color: #FFFFFF; }
    .stButton>button { background: #1A237E !important; color: #00E5FF !important; border-radius: 20px; font-weight: bold; border: 2px solid #00E5FF; }
    .ats-panel { padding: 20px; border-radius: 15px; background: #E3F2FD; border: 1px solid #00E5FF; margin-bottom: 20px; color: #1A237E; }
    .footer-zip { position: fixed; left: 0; bottom: 0; width: 100%; background: #1A237E; color: white; text-align: center; padding: 10px; font-size: 12px; z-index: 999; }
</style>
""", unsafe_allow_html=True)

def render_zipngo_logo(height=200):
    logo_html = """
    <div style="background-color: #1A237E; padding: 20px; text-align: center; border-radius: 15px; font-family: sans-serif;">
        <div style="display: flex; align-items: baseline; justify-content: center;">
            <span style="color: white; font-size: 45px; font-weight: 800; letter-spacing: -2px;">zipngo</span>
            <span style="color: #00e5ff; font-size: 45px; margin: 0 5px;">.</span>
            <div style="background: #ff8c00; padding: 2px 12px; border-radius: 8px; position: relative; margin-left: 5px;">
                <span style="color: #00e5ff; font-size: 35px; font-weight: 900;">zaxx</span>
                <span style="position: absolute; top: -25px; right: -10px; font-size: 30px;">👍</span>
            </div>
        </div>
        <hr style="height: 2px; background: white; border: none; margin: 10px 0;">
        <div style="color: white; font-size: 14px; letter-spacing: 5px; text-transform: uppercase;">The power of choice</div>
    </div>
    """
    st.components.v1.html(logo_html, height=height)

# --- ÉTATS ---
if "z_auth" not in st.session_state: st.session_state.z_auth = False
if "z_view" not in st.session_state: st.session_state.z_view = "login"
if "z_email" not in st.session_state: st.session_state.z_email = "candidat@zipngo.com"

# --- PAGE DE CONNEXION / INSCRIPTION ---
if not st.session_state.z_auth:
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        render_zipngo_logo()
        
        if st.session_state.z_view == "login":
            st.text_input("Identifiant (Email)")
            st.text_input("Mot de passe", type="password")
            if st.button("DÉCOLLER"): 
                st.session_state.z_auth = True
                st.rerun()
            
            c1, c2 = st.columns(2)
            c1.button("Créer un compte", on_click=lambda: st.session_state.update({"z_view": "signup"}))
            c2.button("Mot de passe oublié ?", on_click=lambda: st.session_state.update({"z_view": "forgot"}))

        elif st.session_state.z_view == "signup":
            st.subheader("📝 Inscription Candidat")
            st.text_input("Nom & Prénom")
            st.text_input("Email")
            st.text_input("Mot de passe", type="password")
            if st.button("S'INSCRIRE MAINTENANT"):
                st.success("Compte créé avec succès !")
                st.session_state.z_view = "login"
            st.button("← Retour à la connexion", on_click=lambda: st.session_state.update({"z_view": "login"}))

        elif st.session_state.z_view == "forgot":
            st.subheader("Récupération")
            st.text_input("Email de récupération")
            st.button("Envoyer le lien")
            st.button("← Retour", on_click=lambda: st.session_state.update({"z_view": "login"}))

# --- PAGE PRINCIPALE (APPRÈS CONNEXION) ---
else:
    with st.sidebar:
        render_zipngo_logo(height=160)
        menu = st.selectbox("Menu", ["🌍 Offres", "📄 Relooking CV & ATS", "📹 Coaching Vidéo", "⚙️ Mon Profil"])
        if st.button("🚪 Déconnexion"): 
            st.session_state.z_auth = False
            st.rerun()

    if menu == "🌍 Offres":
        st.header("Opportunités mondiales")
        pays = st.selectbox("Filtrer par Pays", ["Madagascar", "France", "International"])
        st.table(pd.DataFrame({'Poste': ['Manager', 'Expert IT'], 'Lieu': [pays, 'Remote']}))

    elif menu == "📄 Relooking CV & ATS":
        st.header("Analyseur ATS")
        f = st.file_uploader("Chargez votre CV (PDF)", type=["pdf"])
        if f:
            st.markdown('<div class="ats-panel">📊 **Score ATS : 42/100** <br> Attention : Les mots-clés sont insuffisants.</div>', unsafe_allow_html=True)
            if st.button("✨ OPTIMISER MON CV"):
                st.success("Optimisation terminée !")
                st.markdown('<div class="ats-panel" style="background:#C8E6C9;">✅ **Nouveau Score : 98/100**</div>', unsafe_allow_html=True)

    elif menu == "📹 Coaching Vidéo":
        st.header("Préparation Entretien")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    elif menu == "⚙️ Mon Profil":
        st.header("Paramètres")
        st.session_state.z_email = st.text_input("Email", value=st.session_state.z_email)
        st.button("Enregistrer les modifications")

st.markdown('<div class="footer-zip">zipngo.zaxx | Propriété de ZAXX Group | © 2026</div>', unsafe_allow_html=True)
