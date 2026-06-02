import streamlit as st, pandas as pd, io, json, re
from supabase import create_client
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

LANGUES = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Portugais", "Chinois", "Japonais", "Russe", "Arabe", "Néerlandais", "Suédois", "Polonais", "Turc", "Coréen", "Hindi", "Vietnamien", "Thaï", "Indonésien", "Grec"]

# --- FONCTIONS DESIGN ---
def appliquer_design_geometrique(pdf, data, style="Classique"):
    themes = {
        "Classique": {"bg": (52, 73, 94), "text": (255, 255, 255), "accent": (52, 73, 94)},
        "Moderne": {"bg": (230, 126, 34), "text": (255, 255, 255), "accent": (230, 126, 34)},
        "Épuré": {"bg": (40, 40, 40), "text": (255, 255, 255), "accent": (40, 40, 40)}
    }
    t = themes.get(style, themes["Classique"])
    h, s, m = data.get('header', {}), data.get('sidebar', {}), data.get('main', {})
    
    pdf.set_fill_color(*t["bg"]); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(*t["text"])
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, str(h.get('nom', 'N/A')), ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, str(h.get('contact', '')))
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, str(s.get('contenu', '')))
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, str(h.get('titre_poste', '')), ln=True)
    pdf.set_draw_color(*t["accent"]); pdf.line(70, 20, 190, 20)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, str(m.get('titre', '')), ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, str(m.get('corps', '')))

# --- UI PRINCIPALE ---
st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span> ATS Premium</h1>", unsafe_allow_html=True)

role = st.sidebar.radio("Choisissez votre espace :", ["Candidat", "Employeur"])

if role == "Candidat":
    tabs = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking ATS", "🌐 Sourcing", "🎤 Entretien"])
    
    with tabs[0]:
        st.subheader("📋 Historique")
        try: st.table(pd.DataFrame(supabase.table("candidatures").select("*").execute().data))
        except: st.write("Aucune donnée.")
        
    with tabs[1]:
        nom = st.text_input("Nom du fichier"); up = st.file_uploader("Upload", type=["pdf"])
        if up and st.button("💾 Enregistrer"):
            try:
                supabase.table("cvs").insert({"nom_fichier": nom, "contenu": up.getvalue().hex(), "user_id": "00000000-0000-0000-0000-000000000000"}).execute()
                st.success("Enregistré !")
            except Exception as e: st.error(f"Erreur : {e}")
            
    with tabs[2]:
        if 'cv_data' not in st.session_state: st.session_state.cv_data = None
        
        metier = st.text_area("Intitulé du poste visé...")
        up_cv = st.file_uploader("Upload CV actuel", type=["pdf"])
        
        if up_cv and metier and st.button("🔍 Scanner mon CV"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_cv.getvalue())).pages])
            prompt = f"Analyse ce CV pour '{metier}'. Retourne uniquement un JSON strict: {{'score': 0-100, 'feedback': '...', 'header': {{'nom', 'contact', 'titre_poste'}}, 'sidebar': {{'contenu'}}, 'main': {{'titre', 'corps'}}}} CV: {txt}"
            res = client.chat.completions.create(messages=[{"role":"user", "content":prompt}], model="llama-3.3-70b-versatile")
            st.session_state.cv_data = json.loads(re.search(r'\{.*\}', res.choices[0].message.content.strip(), re.DOTALL).group())
            
        if st.session_state.cv_data:
            st.metric("Score ATS", f"{st.session_state.cv_data.get('score', 'N/A')}/100")
            st.info(st.session_state.cv_data.get('feedback', ''))
            
            style_choisi = st.selectbox("Style graphique", ["Classique", "Moderne", "Épuré"])
            if st.button("✅ Valider et Télécharger"):
                pdf = FPDF()
                pdf.add_page()
                appliquer_design_geometrique(pdf, st.session_state.cv_data, style=style_choisi)
                st.download_button("⬇️ Télécharger le CV optimisé", pdf.output(dest='S').encode('latin-1'), "CV_Optimise.pdf")

    with tabs[3]:
        domaine = st.text_input("Métier"); emails_input = st.text_area("Emails")
        if st.button("✅ Préparer l'envoi"): st.markdown(f'<a href="mailto:?bcc={emails_input.replace(chr(10),",")}&subject=Candidature&body=Poste {domaine}">📤 Ouvrir messagerie</a>', unsafe_allow_html=True)
    with tabs[4]:
        try:
            for slot in supabase.table("agenda").select("*").execute().data:
                if st.button(f"Réserver {slot['creneau']}", key=slot['id']): st.success("RDV pris !")
        except: st.write("Agenda non disponible.")

elif role == "Employeur":
    st.subheader("💼 Espace Employeur")
    metier = st.text_input("Poste"); langue = st.selectbox("Langue", LANGUES)
    if st.button("✨ Générer IA"): st.write(client.chat.completions.create(messages=[{"role":"user", "content":f"Annonce pour {metier} en {langue}"}], model="llama-3.3-70b-versatile").choices[0].message.content)

st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
