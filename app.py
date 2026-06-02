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
    st.write("Votre plateforme de rédaction et de mise en relation professionnelle.")
    st.divider()
    role = st.radio("Accès :", ["Candidat", "Employeur"])

# --- ESPACE CANDIDAT ---
if role == "Candidat":
    st.subheader("👤 Espace Candidat")
    
    # 1. Dépôt CV (Obligatoire)
    if 'cv_data' not in st.session_state:
        cv_file = st.file_uploader("Étape 1 : Déposez votre CV (PDF) pour démarrer", type=["pdf"])
        if cv_file:
            st.session_state.cv_data = cv_file.getvalue()
            st.rerun()
    
    # 2. Création de compte via Email (Identifiant)
    elif 'user_email' not in st.session_state:
        st.success("CV reçu.")
        st.info("Étape 2 : Entrez votre email pour créer votre compte (identifiant).")
        email = st.text_input("Votre adresse email")
        if st.button("Créer mon compte"):
            if email:
                st.session_state.user_email = email
                st.rerun()
    
    # 3. Outils de rédaction et Scoring
    else:
        st.write(f"Connecté : **{st.session_state.user_email}**")
        pdf_reader = PdfReader(io.BytesIO(st.session_state.cv_data))
        txt_cv = "".join([page.extract_text() for page in pdf_reader.pages])
        
        poste = st.text_input("Intitulé du poste visé")
        
        if st.button("✨ Générer mes solutions de rédaction"):
            with st.spinner("Analyse et rédaction en cours..."):
                prompt = f"""
                Analyse ce CV pour le poste '{poste}'. 
                Retourne un JSON avec :
                1. 'score': Note sur 100 de correspondance au poste.
                2. 'accroche': Une accroche percutante.
                3. 'vocabulaire': Liste des 10 termes techniques/mots-clés indispensables pour ce métier précis.
                4. 'parcours_revisite': Réécriture professionnelle et valorisée de l'expérience, utilisant le vocabulaire métier.
                CV : {txt_cv}
                """
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                data = json.loads(re.search(r'\{.*\}', res.choices[0].message.content.strip(), re.DOTALL).group())
                st.session_state.solutions = data
        
        if 'solutions' in st.session_state:
            sol = st.session_state.solutions
            st.metric("Score de correspondance", f"{sol['score']}/100")
            st.subheader("🎯 Accroche stratégique")
            st.code(sol['accroche'], language='text')
            st.subheader("🛠 Vocabulaire technique métier")
            st.info(", ".join(sol['vocabulaire']))
            st.subheader("💼 Parcours réécrit (Prêt à copier)")
            st.code(sol['parcours_revisite'], language='text')
            
            st.download_button("⬇️ Télécharger mes solutions", 
                               data=f"ACCROCHE:\n{sol['accroche']}\n\nVOCABULAIRE MÉTIER:\n{', '.join(sol['vocabulaire'])}\n\nPARCOURS:\n{sol['parcours_revisite']}", 
                               file_name="mes_solutions_candidature.txt")

# --- ESPACE EMPLOYEUR ---
elif role == "Employeur":
    st.subheader("💼 Espace Employeur")
    with st.form("form_employeur"):
        email = st.text_input("Email professionnel (identifiant)")
        poste = st.text_input("Poste à pourvoir")
        if st.form_submit_button("Valider et Créer l'offre"):
            st.session_state.user_email = email
            st.success(f"Offre pour {poste} enregistrée.")

# --- CONDITIONS ---
st.markdown("---")
if st.checkbox("J'accepte les conditions d'utilisation"):
    st.caption("Gratuité 3 mois. Optimisation : 1 fois/mois. Prospection : 20 messages/mois.")
    c1, c2 = st.columns(2)
    c1.link_button("Pass Premium Candidat", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
    c2.link_button("Pass Premium Recruteur", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
