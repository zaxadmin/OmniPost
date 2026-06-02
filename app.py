import streamlit as st, pandas as pd, io, json, re
from supabase import create_client
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def nettoyer_texte(valeur):
    if isinstance(valeur, list):
        return ", ".join([str(item) for item in valeur])
    return str(valeur).replace("['", "").replace("']", "").replace("', '", ", ").replace('["', "").replace('"]', "").replace('", "', ", ")

def appliquer_design_geometrique(pdf, data):
    h, s, m = data.get('header', {}), data.get('sidebar', {}), data.get('main', {})
    
    # Première page
    pdf.add_page()
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    
    # Colonne gauche
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, nettoyer_texte(h.get('nom', 'N/A')), ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, nettoyer_texte(h.get('contact', '')))
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "ACCROCHE", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, nettoyer_texte(s.get('accroche', '')))
    
    # Colonne droite
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, nettoyer_texte(h.get('titre_poste', '')), ln=True)
    pdf.set_draw_color(52, 73, 94); pdf.line(70, 20, 190, 20)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, nettoyer_texte(m.get('titre', '')), ln=True)
    
    # Contenu détaillé (multi_cell gère le saut de page automatique)
    pdf.set_xy(70, 45)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(130, 7, nettoyer_texte(m.get('corps', '')))

st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span> ATS Premium</h1>", unsafe_allow_html=True)

if 'cv_data' not in st.session_state: st.session_state.cv_data = None

if st.sidebar.radio("Espace :", ["Candidat", "Employeur"]) == "Candidat":
    with st.tabs(["📂", "📄", "✨ Relooking ATS", "🌐", "🎤"])[2]:
        metier = st.text_area("Intitulé du poste visé...")
        up_cv = st.file_uploader("Upload CV actuel", type=["pdf"])
        
        if up_cv and metier and st.button("🔍 Analyser et Réécrire"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
            prompt = f"""
            Tu es un rédacteur CV expert. Analyse le CV suivant pour le poste '{metier}' :
            1. Rédige une accroche stratégique adaptée.
            2. REÉCRIS L'INTÉGRALITÉ des expériences professionnelles, n'en omet aucune, rends le contenu exhaustif et détaillé.
            3. Retourne un JSON strict :
            {{"score": 85, "recommandations": ["..."], "accroche": "...", 
              "header": {{"nom": "Liliane RAKOTOBE", "contact": "06 12 40 54 91", "titre_poste": "{metier}"}}, 
              "sidebar": {{"accroche": "..."}}, 
              "main": {{"titre": "Parcours Professionnel", "corps": "Texte complet et détaillé de toutes les expériences..."}}}}
            CV : {txt}
            """
            res = client.chat.completions.create(messages=[{"role":"user", "content":prompt}], model="llama-3.3-70b-versatile")
            st.session_state.cv_data = json.loads(re.search(r'\{.*\}', res.choices[0].message.content.strip(), re.DOTALL).group())
            
        if st.session_state.cv_data:
            st.metric("Score ATS", f"{st.session_state.cv_data.get('score', 'N/A')}/100")
            st.subheader("🛠️ Contenu réécrit :")
            st.info(st.session_state.cv_data.get('main', {}).get('corps', ''))
            
            if st.button("✅ Télécharger le CV complet en PDF"):
                pdf = FPDF()
                appliquer_design_geometrique(pdf, st.session_state.cv_data)
                st.download_button("⬇️ Télécharger PDF", pdf.output(dest='S').encode('latin-1'), "CV_Complet_Optimise.pdf")
