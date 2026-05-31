import streamlit as st
import datetime
import pandas as pd
import io
import json
import urllib.parse
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- FONCTIONS ---
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse pour le poste '{metier}'. Retourne uniquement un JSON structuré avec: 'header', 'sidebar', 'main', 'mots_cles_ajoutes'. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    # Ligne unifiée et corrigée pour éviter l'erreur de syntaxe
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("```", ""))

def appliquer_design_geometrique(pdf, data):
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, data['header']['nom'], ln=True)
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, data['header']['titre_poste'], ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, data['main']['titre'], ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, data['main']['corps'])

def trier_candidats_auto(offre_data):
    profils = supabase.table("candidats").select("*").execute().data
    for p in profils:
        prompt = "Compare le CV: {} et l'Offre: {}. Score 0-100. Retourne un JSON strictement comme ceci: {{\"score\": 0}}".format(p.get('cv_text', 'Non disponible'), offre_data)
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        try:
            score = json.loads(res.choices[0].message.content.replace("```json", "").replace("```", "")).get('score', 0)
            statut = "Matchs" if score >= 50 else "Vivier"
            supabase.table("candidats").update({"statut": statut, "score": score}).eq("id", p['id']).execute()
        except: continue

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)
st.session_state.langue = st.sidebar.selectbox("🌐 Langue", ["Français", "English (US)", "Malagasy"])

tab_candidat, tab_employeur = st.tabs(["🚀 Espace Candidat", "💼 Espace Recruteur"])

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📄 CVs", "✨ Relooking", "🌐 Sourcing", "🎤 Entretien"])
    with dossiers[0]:
        st.subheader("📂 Historique des envois")
        res = supabase.table("sourcing").select("email_destinataire, date").execute()
        if res.data: st.table(pd.DataFrame(res.data))
    with dossiers[2]:
        metier = st.text_input("Poste visé")
        up = st.file_uploader("Upload CV", type=["pdf"])
        if up and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            st.download_button("⬇️ Télécharger CV", data=pdf.output(dest='S').encode('latin-1'), file_name="CV.pdf")
    with dossiers[3]: # SOURCING
        st.subheader("🌐 Prospection Spontanée")
        st.info("Utilisation d'IA pour identifier des cibles professionnelles.")
        domaines = ["Restauration", "Informatique", "BTP", "Commerce"]
        cat = st.selectbox("Domaine", domaines)
        ville = st.text_input("Ville cible")
        if st.button("🔍 Rechercher 20 nouveaux contacts") and ville:
            prompt = f"Génère une liste de 20 adresses emails professionnelles pour le secteur '{cat}' à '{ville}'. Utilise un format conforme aux usages légaux (ex: nom.prenom@entreprise.fr). Retourne uniquement la liste séparée par des virgules."
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.session_state.emails = [e.strip() for e in res.split(',')]
            st.rerun()
        if 'emails' in st.session_state:
            up_cv = st.file_uploader("CV en PJ", type=["pdf"])
            if st.button("🚀 Envoyer à la liste") and up_cv:
                resend.Emails.send({"from": "contact@zipngo.zaxx.app", "to": st.session_state.emails[0], "bcc": st.session_state.emails[1:20], "subject": "Candidature", "text": "...", "attachments": [{"filename": "CV.pdf", "content": list(up_cv.getvalue())}]})
                for e in st.session_state.emails[:20]: supabase.table("sourcing").insert({"email_destinataire": e, "date": str(datetime.date.today())}).execute()
                st.success("Campagne envoyée avec succès !")

with tab_employeur:
    st.subheader("📢 Création et Dispatch automatique")
    with st.container():
        col1, col2 = st.columns(2)
        titre = col1.text_input("Intitulé du poste")
        ville = col2.text_input("Ville")
        if st.button("✨ Publier et Dispatcher les profils"):
            offre_full = f"{titre} à {ville}"
            supabase.table("offres").insert({"titre": titre, "details": offre_full}).execute()
            trier_candidats_auto(offre_full)
            st.success("Base dispatchée !")
            st.rerun()

    tiroirs = st.tabs(["🔥 Matchs", "📂 Vivier", "📅 Entretiens"])
    with tiroirs[0]:
        for c in supabase.table("candidats").select("*").gte("score", 50).execute().data:
            with st.expander(f"{c.get('nom_candidat')} - Score: {c.get('score')}%"):
                if st.button(f"👍 Offrir Entretien", key=f"m_{c['id']}"): 
                    supabase.table("candidats").update({"statut": "Entretien"}).eq("id", c['id']).execute()
                    st.rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; font-family: sans-serif;'>
    <p>Créé par <b>Liliane RAKOTOBE</b> | Propulsé par <b>zaxx.app</b></p>
    <p>Besoin d'assistance ? 
       <a href='mailto:creationsites06@gmail.com' style='text-decoration: none;'>
           📧 creationsites06@gmail.com
       </a>
    </p>
</div>
""", unsafe_allow_html=True)
