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
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    h, s, m = data.get('header', {}), data.get('sidebar', {}), data.get('main', {})
    
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, nettoyer_texte(h.get('nom', 'N/A')), ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, nettoyer_texte(h.get('contact', '')))
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "ACCROCHE", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, nettoyer_texte(s.get('accroche', '')))
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, nettoyer_texte(h.get('titre_poste', '')), ln=True)
    pdf.set_draw_color(52, 73, 94); pdf.line(70, 20, 190, 20)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, nettoyer_texte(m.get('titre', '')), ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, nettoyer_texte(m.get('corps', '')))

st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span> ATS Premium</h1>", unsafe_allow_html=True)

if 'cv_data' not in st.session_state: st.session_state.cv_data = None

if st.sidebar.radio("Espace :", ["Candidat", "Employeur"]) == "Candidat":
    with st.tabs(["📂", "📄", "✨ Relooking ATS", "🌐", "🎤"])[2]:
        metier = st.text_area("Intitulé du poste visé...")
        up_cv = st.file_uploader("Upload CV actuel", type=["pdf"])
        
        if up_cv and metier and st.button("🔍 Analyser et Réécrire mon CV"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
            prompt = f"""
            Tu es un rédacteur CV expert. Analyse le CV suivant pour le poste '{metier}' :
            1. Rédige une accroche stratégique (profil professionnel) adaptée au poste.
            2. REÉCRIS les expériences professionnelles pour mettre en valeur les résultats et utiliser les mots-clés du poste.
            3. Retourne un JSON strict :
            {{
                "score": (note de 0 à 100),
                "recommandations": ["liste de conseils stratégiques"],
                "accroche": "Ta phrase d'accroche rédigée",
                "header": {{"nom": "Liliane RAKOTOBE", "contact": "06 12 40 54 91", "titre_poste": "{metier}"}},
                "sidebar": {{"accroche": "La phrase rédigée ci-dessus"}},
                "main": {{"titre": "Expériences Optimisées", "corps": "Tes expériences réécrites de manière professionnelle et percutante"}}
            }}
            CV : {txt}
            """
            res = client.chat.completions.create(messages=[{"role":"user", "content":prompt}], model="llama-3.3-70b-versatile")
            st.session_state.cv_data = json.loads(re.search(r'\{.*\}', res.choices[0].message.content.strip(), re.DOTALL).group())
            
        if st.session_state.cv_data:
            st.metric("Score ATS", f"{st.session_state.cv_data.get('score', 'N/A')}/100")
            
            st.subheader("🛠️ Réécriture réelle de votre contenu :")
            st.info(st.session_state.cv_data.get('main', {}).get('corps', ''))
            
            st.subheader("🎯 Conseils stratégiques :")
            for rec in st.session_state.cv_data.get('recommandations', []):
                st.write(f"- {rec}")
            
            if st.button("✅ Télécharger le CV réécrit"):
                pdf = FPDF()
                pdf.add_page()
                appliquer_design_geometrique(pdf, st.session_state.cv_data)
                st.download_button("⬇️ Télécharger PDF", pdf.output(dest='S').encode('latin-1'), "CV_Optimise.pdf")
