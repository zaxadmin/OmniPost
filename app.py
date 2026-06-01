import streamlit as st
import pandas as pd, io, json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTIONS ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

def envoyer_lien_magique(email):
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        st.success(f"Lien magique envoyé à {email}. Vérifiez vos emails.")
    except Exception as e: st.error(f"Erreur : {e}")

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse pour le poste '{metier}'. Retourne uniquement un JSON structuré avec: 'header', 'sidebar', 'main', 'mots_cles_ajoutes'. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("```", ""))

def appliquer_design_geometrique(pdf, data):
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, data['header']['nom'], ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, data['header']['contact'])
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, data['header']['titre_poste'], ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, data['main']['titre'], ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, data['main']['corps'])

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

# Connexion Magique
with st.sidebar:
    st.subheader("🔑 Connexion Lien Magique")
    email_in = st.text_input("Votre email")
    if st.button("Envoyer mon lien"): envoyer_lien_magique(email_in)
    st.markdown("---")
    st.markdown("### 💎 Accès Premium")
    st.link_button("Premium Candidat (6€)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    st.link_button("Premium Recruteur (39€)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

# Tabs
tabs = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "🔄 Matching"])

with tabs[0]:
    st.markdown("### Le Système du Pouce 👍")
    st.write("Cliquez sur le pouce pour débloquer l'agenda, valider la visio, et lever l'anonymat à deux.")

with tabs[1]:
    dossiers = st.tabs(["📄 CVs", "🎤 Entretien"])
    with dossiers[0]:
        nom = st.text_input("Nom du doc")
        up = st.file_uploader("Upload", type=["pdf"])
        if st.button("💾 Enregistrer") and up and nom:
            user = supabase.auth.get_user()
            supabase.table("cvs").insert({"user_id": user.user.id, "nom_fichier": nom, "contenu": str(up.getvalue())}).execute()
            st.success("Enregistré !")
    with dossiers[1]:
        if st.button("👍 Débloquer"): st.session_state.agenda = True

with tabs[2]:
    metier = st.text_input("Métier")
    if st.button("✅ Diffuser"):
        user = supabase.auth.get_user()
        supabase.table("mes_offres").insert({"user_id": user.user.id, "intitule": metier}).execute()

with tabs[3]:
    if st.button("👍 Valider fin entretien"): st.success("Anonymat levé.")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
