import streamlit as st
import datetime
import PyPDF2
from fpdf import FPDF
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS (Texture 3D Wave & Relief + Icônes) ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {
        background: linear-gradient(135deg, #f0f2f6 0%, #ffffff 100%);
        background-image: 
            linear-gradient(145deg, rgba(255,255,255,0.4) 10%, transparent 40%),
            linear-gradient(145deg, rgba(0,0,0,0.05) 45%, transparent 55%),
            linear-gradient(145deg, rgba(255,255,255,0.6) 60%, transparent 90%);
    }
    .main .block-container { 
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        padding: 40px !important; 
        border-radius: 25px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1), inset 0 0 0 1px rgba(255,255,255,0.5) !important;
    }
    .brand-title { font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 0.1rem; }
    .zip { color: #000080; } .ngo { color: #00FFFF; }
    .stButton>button { background-color: #007BFF !important; color: white !important; border-radius: 12px !important; width: 100%; }
    .mail-icon { font-size: 1.5rem; text-decoration: none; color: #007BFF; transition: 0.3s; }
    .mail-icon:hover { color: #0056b3; }
    </style>
    <div class="brand-title"><span class="zip">zip</span><span class="ngo">ngo</span> 👍</div>
    """, unsafe_allow_html=True)

# --- FONCTIONS ---
def creer_pdf_securise(contenu, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=contenu)
    return pdf.output(dest='S').encode('latin-1')

def analyser_ats(text):
    score = min(100, len(text) // 50)
    return score, "Mots-clés optimisés."

def executer_scrapping(is_premium):
    limite = 1000 if is_premium else 20
    return [f"Profil Candidat {i}" for i in range(1, limite + 1)]

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({
        "auth": False, "profile_completed": False, "user_type": "Candidat", 
        "pouce_employeur": False, "pouce_candidat": False, "premium": False, "mode_remote": False
    })

# --- NAVIGATION ---
if not st.session_state.auth:
    st.markdown("### Bienvenue sur zipngo.")
    st.write("Plateforme de mise en relation professionnelle qui place les compétences et la confidentialité au premier plan")
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"):
        st.session_state.update({"auth": True, "user_type": role})
        st.rerun()

elif not st.session_state.profile_completed:
    st.header(f"Mode d'emploi : {st.session_state.user_type}")
    if st.session_state.user_type == "Candidat":
        st.info("1. Déposez votre CV. 2. L'IA l'adapte. 3. Propulsez anonymement.")
    else:
        st.info("1. Scrappez des profils. 2. Diffusez vos offres. 3. Validez les matchs pour démasquer.")
    if st.button("Valider profil"): st.session_state.profile_completed = True; st.rerun()

else:
    t = {"dash": "Tableau de bord", "label": "Profil/ATS", "scrap": "Scrapping", "match": "Entretiens", "cgv": "📜 CGV & Mentions", "acc": "Mon Compte"}
    with st.sidebar:
        if st.checkbox("Activer Premium"): st.session_state.premium = True
        if st.session_state.premium: st.checkbox("🌍 Mode Remote (Illimité)", key="mode_remote")
        menu = st.radio("Navigation", list(t.values()))
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    if menu == t["dash"]:
        st.header("Tableau de bord")
    
    elif menu == t["label"]:
        st.header("Profil & ATS")
        cv = st.file_uploader("Mon CV", type="pdf")
        mobilite = st.radio("Mobilité :", ["💼 Présentiel (Pays)", "🌍 À distance (Remote)"], horizontal=True)
        if cv and st.button("✨ Analyser & Adapter"):
            score, sugg = analyser_ats("contenu_cv")
            st.write(f"Score ATS : {score}%")
            st.download_button("📥 Télécharger CV optimisé", data=creer_pdf_securise("CV Optimisé", "CV"), file_name="cv.pdf")

    elif menu == t["scrap"]:
        st.header("Scrapping")
        limite = 1000 if st.session_state.mode_remote else 20
        if st.button(f"🔍 Scrapper ({limite} max)"):
            st.write(executer_scrapping(st.session_state.premium))

    elif menu == t["cgv"]:
        st.header("📜 CGV & Mentions Légales")
        st.write("ZipnGo est un intermédiaire technique. L'anonymat est garanti par double accord.")

    elif menu == t["match"]:
        if st.session_state.user_type == "Employeur":
            if st.button("👍 Valider ce profil"): st.session_state.pouce_employeur = True
        else:
            if st.button("👍 Accepter cet entretien"): st.session_state.pouce_candidat = True
        
        if st.session_state.pouce_employeur and st.session_state.pouce_candidat:
            st.balloons()
            st.success("Accord mutuel ! Anonymat levé.")
            st.download_button("🔓 Télécharger dossier complet", data=creer_pdf_securise("Données réelles...", "Dossier"), file_name="contact.pdf")
            st.link_button("🎥 Rejoindre la salle", "https://meet.jit.si/zipngo")
            if st.button("🔄 Réactiver l'anonymat / Retour tableau de bord"):
                for k in ["pouce_employeur", "pouce_candidat"]: st.session_state[k] = False
                st.rerun()

    elif menu == t["acc"]:
        st.header("Mon Compte")
        st.markdown('<a href="mailto:creationsites06@gmail.com" class="mail-icon">📧 creationsites06@gmail.com</a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
