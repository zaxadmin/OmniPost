import streamlit as st
import pdfplumber
from groq import Groq
from fpdf import FPDF
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURATION IA SÉCURISÉE ---
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    client_ia = Groq(api_key=GROQ_KEY)
except Exception:
    st.error("⚠️ Configuration IA manquante dans les Secrets Streamlit.")
    st.stop()

# --- 2. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 3. STYLE CSS AVANCÉ (MARINE, CYAN & TEXTES BLANCS) ---
st.markdown("""
<style>
    /* Fond dégradé moderne */
    .stApp {
        background: linear-gradient(160deg, #001529 0%, #002147 50%, #0a3d62 100%);
        color: white !important;
    }

    /* Forcer tout le texte en blanc par défaut */
    .stApp, p, span, label, div {
        color: white !important;
    }

    /* Conteneurs transparents avec bordure Cyan */
    [data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.2);
    }

    /* Style du Logo et Titres */
    .main-logo-text { font-size: 60px !important; font-weight: 900; color: #00E5FF !important; text-align: center; margin: 0; letter-spacing: -2px; }
    .power-title { text-align: center; color: #FFFFFF !important; font-size: 16px; font-weight: 400; margin-top: -15px; text-transform: uppercase; letter-spacing: 3px; }
    
    /* Boutons de paiement Premium (Cyan & Marine) */
    .pay-btn > div > button {
        background-color: #00E5FF !important; 
        color: #002147 !important; 
        border: none !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 70px !important;
        width: 100%;
        border-radius: 15px !important;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
    }
    
    /* Boutons Standards (Bordure Cyan, Texte Blanc) */
    .stButton>button {
        border-radius: 10px !important;
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #00E5FF !important;
    }
    .stButton>button:hover {
        background-color: #00E5FF !important;
        color: #002147 !important;
    }

    /* Alertes (Remplacer le fond rouge/jaune par du sombre/cyan pour le texte blanc) */
    .stAlert {
        background-color: rgba(0, 33, 71, 0.8) !important;
        border: 1px solid #00E5FF !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. FONCTIONS TECHNIQUES ---
def extraire_texte_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            return "".join([page.extract_text() for page in pdf.pages])
    except Exception as e: return f"Erreur : {e}"

def generer_pdf_cv(texte_optimise):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CV OPTIMISE - ZIPNGO ZAXX", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    texte_propre = texte_optimise.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, texte_propre)
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- 5. INITIALISATION ---
