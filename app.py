import streamlit as st, pandas as pd, io, json, re, datetime
from supabase import create_client
from groq import Groq
from pypdf import PdfReader
# import resend  # Assurez-vous d'avoir installé 'resend'

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | Solutions Professionnelles", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
# resend.api_key = st.secrets["RESEND_API_KEY"]

# --- UI PRINCIPALE ---
st.markdown("<h1 style='text-align: center; color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

with st.sidebar:
    role = st.radio("Accès :", ["Candidat", "Employeur"])

# --- ESPACE CANDIDAT ---
if role == "Candidat":
    st.subheader("👤 Espace Candidat")
    
    # Gestion des onglets
    dossiers = st.tabs(["Optimisation", "Suivi", "CVs", "Prospection", "Entretien"])
    
    # 1. Optimisation (votre logique précédente)
    with dossiers[0]:
        cv_file = st.file_uploader("Déposez votre CV", type=["pdf"])
        if cv_file:
            st.session_state.cv_data = cv_file.getvalue()
            # ... (logique d'optimisation ici)
            st.write("Section Optimisation active")

    # 2. SOURCING (Nouveau)
    with dossiers[3]: 
        st.subheader("🌐 Prospection Spontanée")
        domaines = ["Restauration & Fast-Food", "Informatique & Tech", "Hôtellerie & Tourisme", "Santé & Services à la personne", "Commerce & Distribution", "BTP & Immobilier", "Logistique & Transport", "Finance & Juridique", "Marketing, Com & Art", "Industrie & Agriculture", "Administration publique"]
        
        col1, col2, col3 = st.columns([1, 1, 1])
        cat = col1.selectbox("Domaine élargi", sorted(domaines))
        ville = col2.text_input("Ville cible")
        dist = col3.slider("Rayon (km)", 0, 100, 20)
        
        if st.button("🔍 Rechercher 20 nouveaux contacts") and ville:
            deja = [i['email_destinataire'] for i in supabase.table("sourcing").select("email_destinataire").execute().data]
            prompt = f"Donne 20 adresses emails professionnelles pour le domaine '{cat}' à '{ville}'. Exclus : {','.join(deja)}. Format : liste d'emails séparés par des virgules."
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.session_state.emails = [e.strip() for e in res.replace('\n', '').split(',')]
            st.rerun()
            
        if 'emails' in st.session_state:
            st.write(f"Cibles : {', '.join(st.session_state.emails)}")
            msg = st.text_area("Message :", f"Madame, Monsieur, je porte un vif intérêt à votre établissement à {ville} dans le secteur de {cat}. Fort(e) d'une expérience pertinente, je vous propose ma candidature. Vous trouverez mon CV en pièce jointe.", height=200)
            up_cv = st.file_uploader("CV en PJ", type=["pdf"])
            if st.button("🚀 Envoyer à 20 contacts") and up_cv:
                # resend.Emails.send({...}) # Décommentez après config
                for e in st.session_state.emails[:20]: 
                    supabase.table("sourcing").insert({"email_destinataire": e, "date": str(datetime.date.today())}).execute()
                st.success("✅ Campagne envoyée !")

    # 3. ENTRETIEN (Nouveau)
    with dossiers[4]:
        st.subheader("🎤 Simulateur d'entretien")
        if st.button("Démarrer la simulation"):
            st.session_state.quest = client.chat.completions.create(messages=[{"role": "user", "content": "Pose 3 questions d'entretien pour ce profil."}], model="llama-3.3-70b-versatile").choices[0].message.content
        if 'quest' in st.session_state:
            st.write(st.session_state.quest)
            rep = st.text_area("Votre réponse :")
            if st.button("Évaluer"):
                score = client.chat.completions.create(messages=[{"role": "user", "content": f"Note cette réponse sur 20 : {rep}"}], model="llama-3.3-70b-versatile").choices[0].message.content
                st.info(score)

# --- ESPACE EMPLOYEUR ---
elif role == "Employeur":
    st.subheader("💼 Espace Employeur")
    # ... (formulaire inchangé)

st.markdown("---")
st.markdown("<div style='text-align: center;'>Créatrice : <b>Liliane RAKOTOBE</b></div>", unsafe_allow_html=True)
