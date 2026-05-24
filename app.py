import streamlit as st
import datetime
import PyPDF2
from fpdf import FPDF
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- FONCTIONS DE PRODUCTION (ATS, PDF, ANONYMISATION) ---
def creer_pdf_securise(contenu, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=contenu)
    return pdf.output(dest='S').encode('latin-1')

def analyser_et_relooker_cv(text):
    score = min(100, len(text) // 50) 
    suggestions = "- Optimiser les mots-clés ATS\n- Structurer les expériences par compétences\n- Clarifier le titre du poste"
    return score, suggestions

def anonymiser_texte(texte):
    # Regex pour masquer email et tel
    texte = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL MASQUÉ]', texte)
    texte = re.sub(r'(\d{2}[- ]?){4}\d{2}', '[TEL MASQUÉ]', texte)
    return texte

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({
        "auth": False, "premium": False, "profile_completed": False, 
        "user_type": "Candidat", "pouce_employeur": False, "pouce_candidat": False,
        "entretien_ok": False, "rdv_confirme": False
    })

# --- STYLE CSS ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #f6f9fc 0%, #ffffff 100%); }
    .brand-title { font-size: 3rem; font-weight: 800; text-align: center; margin-bottom: 0.1rem; }
    .zip { color: #000080; } .ngo { color: #00FFFF; }
    .app-url { font-size: 0.95rem; color: #6c757d; text-align: center; margin-bottom: 2rem; }
    .stButton>button { background-color: #007BFF !important; color: white !important; border-radius: 12px !important; width: 100%; }
    </style>
    <div class="brand-title"><span class="zip">zip</span><span class="ngo">ngo</span> 👍</div>
    <div class="app-url">.zaxx.app</div>
    """, unsafe_allow_html=True)

# --- PAGE DE CONNEXION ---
if not st.session_state.auth:
    st.markdown("### Bienvenue dans l'application qui révolutionne le recrutement.")
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer dans l'application"):
        st.session_state.update({"auth": True, "user_type": role})
        st.rerun()

# --- ONBOARDING ---
elif not st.session_state.profile_completed:
    st.header("✨ Finalisez votre inscription")
    with st.form("onboarding"):
        nom = st.text_input("Nom & Prénom")
        tel = st.text_input("Téléphone")
        email_pro = st.text_input("Email de contact")
        if st.session_state.user_type == "Employeur":
            entreprise = st.text_input("Nom de l'entreprise")
        else:
            secteur = st.selectbox("Secteur d'activité", ["Tech", "Finance", "Santé", "Autre"])
        if st.form_submit_button("Valider mes informations"):
            st.session_state.profile_completed = True
            st.rerun()
    st.stop()

# --- APPLICATION ---
else:
    t = {"dash": "Tableau de bord", "label": "Profil", "prop": "Propulsion", "match": "Entretiens", "off": "Diffusion", "acc": "Mon Compte"}
    with st.sidebar:
        if st.session_state.premium: st.success("✨ Premium Actif")
        else: st.warning("⚠️ Essai gratuit")
        menu = st.radio("Navigation", list(t.values()))
        with st.expander("📖 Mode d'emploi"): st.write("Déposez votre CV/Offre. L'IA optimise. Validez mutuellement (Pouce) pour lever l'anonymat.")
        with st.expander("📜 CGV"): st.write("Mise en veille après 90j sans Premium.")
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    if menu == t["dash"]:
        st.header(t["dash"])
        st.info("Guide : " + ("Optimisez votre CV, propulsez-le anonymement." if st.session_state.user_type == "Candidat" else "Diffusez anonymement, validez les matchs."))

    elif menu == t["label"]:
        uploaded = st.file_uploader("Déposer mon CV", type="pdf")
        if uploaded:
            text = "".join([page.extract_text() for page in PyPDF2.PdfReader(uploaded).pages])
            if st.button("✨ Optimiser avec l'IA"):
                score, sugg = analyser_et_relooker_cv(text)
                st.write(f"✅ Score ATS : {score}%.")
                st.write(sugg)

    elif menu == t["prop"]:
        if st.button("🚀 Propulser ma candidature"): st.success("Transmis. Identité protégée.")

    elif menu == t["match"]:
        # LOGIQUE DOUBLE POUCE
        if st.session_state.user_type == "Employeur":
            if st.button("👍 Valider ce candidat"): st.session_state.pouce_employeur = True
        else:
            if st.button("👍 Accepter cet entretien"): st.session_state.pouce_candidat = True
        
        if st.session_state.pouce_employeur and st.session_state.pouce_candidat:
            st.balloons()
            st.success("Accord mutuel ! Anonymat levé.")
            st.download_button("🔓 Télécharger le dossier complet", data=creer_pdf_securise("Contact réel...", "Dossier"), file_name="contact.pdf")
            st.link_button("🎥 Rejoindre la salle", "https://meet.jit.si/zipngo")
            if st.button("Terminer la mission et reset anonymat"):
                for key in ["pouce_employeur", "pouce_candidat", "entretien_ok"]: st.session_state[key] = False
                st.rerun()

    elif menu == t["off"]:
        if st.checkbox("🌍 Offre Remote"): st.success("Portée mondiale.")
        if st.button("📢 Diffuser mon offre"): st.balloons()

    elif menu == t["acc"]:
        st.header(t["acc"])
        st.link_button("📧 Support & Suppression", "mailto:creationsites06@gmail.com")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
