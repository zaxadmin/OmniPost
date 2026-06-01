import streamlit as st, pandas as pd, io, json, re, urllib.parse
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

LANGUES = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Portugais", "Chinois", "Japonais", "Russe", "Arabe", "Néerlandais", "Suédois", "Polonais", "Turc", "Coréen", "Hindi", "Vietnamien", "Thaï", "Indonésien", "Grec"]

# --- FONCTIONS ---
def envoyer_lien_magique(email):
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        st.success(f"Lien envoyé à {email}.")
    except Exception as e: st.error(f"Erreur : {e}")

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse ce CV pour {metier}. Retourne JSON: {{header, sidebar, main, mots_cles_ajoutes}}. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    content = res.choices[0].message.content.strip()
    return json.loads(re.search(r'\{.*\}', content, re.DOTALL).group())

def appliquer_design_geometrique(pdf, data):
    h, s, m = data.get('header', {}), data.get('sidebar', {}), data.get('main', {})
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F'); pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, h.get('nom', 'N/A'), ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, h.get('contact', ''))
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, s.get('contenu', ''))
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, h.get('titre_poste', ''), ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, m.get('titre', ''), ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, m.get('corps', ''))

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

with st.sidebar
