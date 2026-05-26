import streamlit as st
import datetime
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")

# Initialisation des clients avec secrets
@st.cache_resource
def get_clients():
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    return supabase, groq_client

supabase, groq_client = get_clients()

# --- FONCTIONS ---
def creer_pdf_cv_pro(texte_ia, nom_fichier):
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

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-top: 50px;'>© 2026 zipngo.zaxx.app | <strong>Créatrice : Liliane RAKOTOBE</strong></div>", unsafe_allow_html=True)

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[0]: # Candidatures
        st.subheader("📊 Mon Statut")
        try:
            historique = supabase.table("candidatures").select("*").order("date", desc=True).execute().data
            for c in historique:
                st.write(f"📅 {c.get('date')} | **{c.get('entreprise')}** - Statut: {c.get('statut')}")
        except Exception:
            st.info("Aucun historique trouvé ou base inaccessible.")

    with dossiers[3]: # ✨ Relooking
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            reader = PdfReader(up)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            if st.button("🚀 Optimiser mon CV"):
                with st.spinner("Analyse IA en cours..."):
                    res = groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Optimise ce CV pour les ATS : {text}"}], 
                        model="llama-3.3-70b-versatile"
                    )
                    cv_opti = res.choices[0].message.content
                    st.text_area("Résultat", value=cv_opti, height=300)
                    supabase.table("cvs").insert({"nom_fichier": up.name, "contenu": cv_opti}).execute()
                    st.success("✅ Enregistré dans Supabase !")

    with dossiers[4]: # 🌐 Sourcing
        st.subheader("🌐 Prospection Spontanée")
        secteur = st.text_input("Secteur")
        ville = st.text_input("Ville")
        if st.button("🔍 Rechercher"):
            res = groq_client.chat.completions.create(messages=[{"role": "user", "content": f"Emails pour {secteur} à {ville}"}], model="llama-3.3-70b-versatile")
            st.session_state.emails = res.choices[0].message.content
        
        if 'emails' in st.session_state:
            st.write(st.session_state.emails)
            if st.button("🚀 Ajouter aux candidatures"):
                supabase.table("candidatures").insert({"entreprise": secteur, "statut": "ENVOYÉ", "date": str(datetime.date.today())}).execute()
                st.success("Candidature enregistrée !")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
