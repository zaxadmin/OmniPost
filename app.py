import streamlit as st
import datetime
import re
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- FONCTIONS ---
def creer_pdf_cv_pro(texte_ia, nom_fichier, style):
    pdf = FPDF()
    pdf.add_page()
    if style == "Classique": pdf.set_font("Times", 'B', 16)
    elif style == "Moderne": pdf.set_font("Arial", 'B', 18)
    else: pdf.set_font("Courier", 'B', 16)
    pdf.cell(200, 10, txt="Mon CV Optimisé", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=texte_ia)
    pdf.output(nom_fichier)

def afficher_cgv():
    st.markdown("### 📜 CGV (Conditions Générales de Vente)\n1. Accès Candidat 6€/3mois | Recruteur 39€/mois.\n2. Limites Gratuit : 1 CV/mois, 1 campagne/mois.\n3. Premium : 3 CVs/semaine, 20 mails/jour.")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#333333; font-size: 14px; margin-top: 0px;'>.zaxx.app</p>", unsafe_allow_html=True)

# 1. SÉLECTEUR DE LANGUE
langues = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"]
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue / Select your language", langues, index=0)

# 2. VOTRE SUCCÈS...
st.markdown("<h4 style='color: #4169E1; margin: 20px 0;'>Votre succès professionnel, propulsé par la précision.</h4>", unsafe_allow_html=True)

# 3. BIENVENUE...
st.markdown("""
<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4169E1; margin-bottom: 20px;'>
    <h4 style='margin-top:0;'>Bienvenue sur zipngo</h4>
    L'écosystème intelligent dédié à votre dynamique professionnelle. Que vous soyez en quête de nouvelles opportunités ou en phase de gestion de talents, 
    zipngo agit comme un facilitateur technologique. Nous simplifions la mise en relation et la gestion des parcours.
</div>
""", unsafe_allow_html=True)

# 4. LIRE LES CGV
with st.expander("📜 Lire les CGV"): afficher_cgv()

# 5. ACCEPTER LES CGV
st.checkbox("J'accepte les CGV", key="accept_cgv")

# 6. ACCUEIL/CANDIDAT/EMPLOYEUR
tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.write("Bienvenue dans votre espace d'accueil.")
    st.markdown("<div style='text-align: center; margin-top: 50px;'>© 2026 zipngo.zaxx.app | <strong>Créatrice : Liliane RAKOTOBE</strong></div>", unsafe_allow_html=True)

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[0]:
        st.subheader("📊 Mon Statut & Historique")
        try:
            historique = supabase.table("candidatures").select("*").order("date", desc=True).execute().data
            for c in historique:
                st.write(f"📅 {c.get('date')} | **{c.get('entreprise')}** - Statut: {c.get('statut')}")
        except: st.info("Aucun historique trouvé.")

    with dossiers[3]:
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            if st.button("🔍 Scanner et Analyser le CV"):
                with st.spinner("Analyse ATS en cours..."):
                    reader = PdfReader(up)
                    text = "".join([p.extract_text() for p in reader.pages])
                    res = client.chat.completions.create(messages=[{"role": "user", "content": f"Analyse ATS : {text}"}], model="llama-3.3-70b-versatile")
                    st.session_state.analyse_cv = res.choices[0].message.content
                    st.session_state.texte_original = text
            if 'analyse_cv' in st.session_state:
                st.info(st.session_state.analyse_cv)
                contenu_pro = st.text_area("Optimisation du contenu", value=st.session_state.texte_original, height=300)
                if st.button("✨ Générer version ATS optimisée"):
                    res_opt = client.chat.completions.create(messages=[{"role": "user", "content": f"Optimise pour ATS : {contenu_pro}"}], model="llama-3.3-70b-versatile")
                    st.session_state.texte_final = res_opt.choices[0].message.content
                    st.success("Contenu optimisé prêt !")
                if 'texte_final' in st.session_state:
                    style = st.selectbox("Style de mise en page", ["Classique", "Moderne", "Minimaliste"])
                    if st.button("🚀 Générer et Archiver le CV"):
                        nom_f = f"CV_Optimise_{datetime.date.today()}.pdf"
                        creer_pdf_cv_pro(st.session_state.texte_final, nom_f, style)
                        supabase.table("cvs").insert({"nom_fichier": nom_f, "contenu": st.session_state.texte_final}).execute()
                        st.success(f"✅ {nom_f} archivé !")

    with dossiers[4]:
        st.subheader("🌐 Prospection Spontanée")
        categorie = st.selectbox("Domaine d'activité", ["Restauration", "Hôtellerie", "Commerce", "Santé", "BTP", "Logistique", "Informatique"])
        ville = st.text_input("Ville")
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            st.session_state.emails_trouves = "exemple@email.com" # Simulation
        
        if 'emails_trouves' in st.session_state:
            msg = st.text_area("Message", value="""Madame, Monsieur, 

Je me permets de vous adresser ma candidature spontanée pour rejoindre votre entreprise. 

Cordialement,""", height=250)
            if st.button("🚀 Valider et Envoyer"):
                st.success("✅ Candidatures envoyées !")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
