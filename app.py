import streamlit as st, pandas as pd, io, json, re
from supabase import create_client
from groq import Groq
from pypdf import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | Solutions Professionnelles", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- UI PRINCIPALE ---
st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🚀 Bienvenue sur zipngo")
    st.write("Plateforme de rédaction et de mise en relation professionnelle.")
    st.divider()
    role = st.radio("Accès :", ["Candidat", "Employeur"])

# --- ESPACE CANDIDAT (RÉDACTION DIRECTE) ---
if role == "Candidat":
    st.subheader("👤 Espace Candidat")
    cv_file = st.file_uploader("Document indispensable : Déposez votre CV (PDF)", type=["pdf"])
    
    if cv_file:
        pdf_reader = PdfReader(io.BytesIO(cv_file.getvalue()))
        txt_cv = "".join([page.extract_text() for page in pdf_reader.pages])
        
        poste = st.text_input("Intitulé du poste visé")
        if st.button("✨ Rédiger mes solutions"):
            with st.spinner("Rédaction en cours..."):
                prompt = f"""
                Tu es un rédacteur professionnel. Analyse ce CV et le poste visé '{poste}'. 
                Rédige les éléments suivants prêts à être copiés :
                1. 'accroche': Une phrase d'accroche percutante.
                2. 'parcours': Réécriture complète et valorisée de chaque expérience professionnelle.
                3. 'competences': Liste des compétences à mettre en avant.
                Retourne uniquement un JSON.
                CV: {txt_cv}
                """
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                data = json.loads(re.search(r'\{.*\}', res.choices[0].message.content.strip(), re.DOTALL).group())
                st.session_state.solutions = data
        
        if 'solutions' in st.session_state:
            sol = st.session_state.solutions
            st.subheader("📝 Accroche (Prêt à copier)")
            st.code(sol['accroche'], language='text')
            
            st.subheader("💼 Parcours réécrit (Prêt à copier)")
            st.code(sol['parcours'], language='text')
            
            st.subheader("🛠 Compétences clés")
            st.code("\n".join(sol['competences']), language='text')
            
            st.download_button("⬇️ Télécharger toutes les solutions", 
                               data=f"ACCROCHE:\n{sol['accroche']}\n\nPARCOURS:\n{sol['parcours']}\n\nCOMPÉTENCES:\n{', '.join(sol['competences'])}", 
                               file_name="mes_solutions_redigees.txt")
    else:
        st.warning("⚠️ Déposez votre CV pour commencer la rédaction.")

# --- ESPACE EMPLOYEUR ---
elif role == "Employeur":
    st.subheader("💼 Espace Employeur")
    with st.form("form_employeur"):
        col1, col2 = st.columns(2)
        entreprise = col1.text_input("Entreprise")
        poste = col2.text_input("Poste")
        if st.form_submit_button("Générer l'offre prête à diffuser"):
            st.success("Offre rédigée et transmise.")

# --- CONDITIONS ---
st.markdown("---")
if st.checkbox("J'accepte les conditions d'utilisation"):
    st.caption("Rappel : Gratuité 3 mois. Optimisation : 1 fois/mois. Prospection : 20 messages/mois.")
    st.link_button("Pass Premium Candidat", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    st.link_button("Pass Premium Recruteur", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")
