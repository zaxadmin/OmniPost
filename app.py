import streamlit as st
import datetime
import re
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader
from postgrest.exceptions import APIError

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTION DE SÉCURITÉ ---
def safe_supabase_query(operation):
    try:
        return operation.execute()
    except APIError as e:
        st.error(f"Erreur Supabase (API) : {e.message}")
        return None
    except Exception as e:
        st.error(f"Erreur inattendue : {str(e)}")
        return None

# --- FONCTIONS UTILES ---
def creer_pdf_cv_pro(texte_ia, nom_fichier, style):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Mon CV Optimisé", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=texte_ia)
    pdf.output(nom_fichier)

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app👍</h1>", unsafe_allow_html=True)

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[0]: # 📂 Candidatures
        st.subheader("📊 Mon Statut & Historique")
        res = safe_supabase_query(supabase.table("candidatures").select("*").order("date", desc=True))
        if res and res.data:
            for c in res.data:
                st.write(f"📅 {c.get('date')} | **{c.get('entreprise')}** - Statut: {c.get('statut')}")
        else:
            st.info("Aucun historique ou erreur de connexion.")

    with dossiers[3]: # ✨ Relooking
        up = st.file_uploader("Upload CV (PDF)", type=["pdf"])
        if up and st.button("🔍 Scanner"):
            reader = PdfReader(up)
            text = "".join([p.extract_text() for p in reader.pages])
            st.session_state.texte_original = text
            st.success("CV chargé !")
            
        if 'texte_original' in st.session_state:
            if st.button("🚀 Générer et Archiver"):
                nom_f = f"CV_{datetime.date.today()}.pdf"
                creer_pdf_cv_pro(st.session_state.texte_original, nom_f, "Classique")
                safe_supabase_query(supabase.table("cvs").insert({"nom_fichier": nom_f, "contenu": st.session_state.texte_original}))
                st.success("✅ Archivé !")

    with dossiers[4]: # 🌐 Sourcing
        st.subheader("🌐 Prospection")
        if st.button("Rechercher"):
            res_s = safe_supabase_query(supabase.table("sourcing").select("email_destinataire"))
            st.write("Recherche lancée...")
