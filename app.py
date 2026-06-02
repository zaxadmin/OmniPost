import streamlit as st, pandas as pd, io, json, re
from supabase import create_client
from groq import Groq
from pypdf import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | Plateforme Professionnelle", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- UI PRINCIPALE ---
st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🚀 Bienvenue sur zipngo")
    st.write("Votre partenaire de réussite professionnelle.")
    st.divider()
    role = st.radio("Accès :", ["Candidat", "Employeur"])

# --- ESPACE CANDIDAT ---
if role == "Candidat":
    st.subheader("👤 Espace Candidat")
    
    # Étape 1 : Dépôt CV
    if 'cv_data' not in st.session_state:
        cv_file = st.file_uploader("Étape 1 : Déposez votre CV (PDF) pour démarrer", type=["pdf"])
        if cv_file:
            st.session_state.cv_data = cv_file.getvalue()
            st.rerun()
    
    # Étape 2 : Création de compte via Email
    elif 'user_email' not in st.session_state:
        st.success("CV reçu !")
        st.info("Étape 2 : Entrez votre email pour créer votre compte (identifiant).")
        email = st.text_input("Votre adresse email")
        if st.button("Créer mon compte"):
            if email:
                st.session_state.user_email = email
                st.rerun()
    
    # Étape 3 : Accès aux outils de rédaction
    else:
        st.write(f"Connecté : **{st.session_state.user_email}**")
        pdf_reader = PdfReader(io.BytesIO(st.session_state.cv_data))
        txt_cv = "".join([page.extract_text() for page in pdf_reader.pages])
        
        poste = st.text_input("Intitulé du poste visé")
        if st.button("✨ Rédiger mes solutions"):
            with st.spinner("Analyse et rédaction en cours..."):
                prompt = f"Analyse ce CV pour le poste '{poste}'. Rédige : 1. Accroche. 2. Parcours (réécrit). 3. Compétences. Retourne en JSON. CV: {txt_cv}"
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                data = json.loads(re.search(r'\{.*\}', res.choices[0].message.content.strip(), re.DOTALL).group())
                st.session_state.solutions = data
        
        if 'solutions' in st.session_state:
            sol = st.session_state.solutions
            st.subheader("📝 Accroche (Prêt à copier)")
            st.code(sol['accroche'], language='text')
            st.subheader("💼 Parcours réécrit (Prêt à copier)")
            st.code(sol['parcours'], language='text')
            st.download_button("⬇️ Télécharger mes solutions", data=f"ACCROCHE:\n{sol['accroche']}\n\nPARCOURS:\n{sol['parcours']}", file_name="mes_solutions.txt")

# --- ESPACE EMPLOYEUR ---
elif role == "Employeur":
    st.subheader("💼 Espace Employeur")
    with st.form("form_employeur"):
        email = st.text_input("Votre email professionnel (identifiant)")
        poste = st.text_input("Poste à pourvoir")
        if st.form_submit_button("Valider et Créer l'offre"):
            st.session_state.user_email = email
            st.success(f"Offre pour {poste} enregistrée.")

# --- CONDITIONS ---
st.markdown("---")
if st.checkbox("J'accepte les conditions d'utilisation"):
    st.caption("Gratuité 3 mois. Optimisation : 1 fois/mois. Prospection : 20 messages/mois.")
    c1, c2 = st.columns(2)
    c1.link_button("Pass Premium Candidat (6€)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    c2.link_button("Pass Premium Recruteur (39€)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
