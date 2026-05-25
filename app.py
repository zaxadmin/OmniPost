import streamlit as st
from groq import Groq
from supabase import create_client
import json
from datetime import date
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide")
client_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- SESSION ---
if "auth" not in st.session_state:
    st.session_state.update({"auth": False, "is_premium": False})

# --- UI HAUT DE PAGE ---
col_lang, col_rest = st.columns([1, 5])
with col_lang:
    st.session_state["langue"] = st.selectbox("🌐", ["Français", "English", "Malagasy", "Español", "Deutsch"], label_visibility="collapsed")

if not st.session_state.auth:
    st.markdown('# zip<span style="color:#1E90FF;">ngo</span> 👍', unsafe_allow_html=True)
    st.write("Bienvenue sur zipngo, l'assistant intelligent pour propulser votre carrière ou vos recrutements.")
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer"): st.session_state.update({"auth": True, "user_type": role}); st.rerun()
else:
    # Bouton Premium discret à droite
    if not st.session_state["is_premium"]:
        st.sidebar.link_button("💎 Passer Premium", "https://buy.stripe.com/votre_lien")

    menu = st.sidebar.radio("Navigation", ["Dashboard", "Prospection", "Entretien"])

    if menu == "Dashboard" and st.session_state.user_type == "Candidat":
        st.header("🚀 Espace Candidat")
        st.checkbox("💻 Profil ouvert au Remote", key="remote_status")
        cv_file = st.file_uploader("Upload votre CV (PDF/TXT)")
        job_target = st.text_input("Intitulé du poste visé :")
        if st.button("Optimiser CV"):
            contenu = "Texte du CV extrait..." # Ajoutez une logique PyPDF2 ici
            res = client_groq.chat.completions.create(messages=[{"role":"user", "content": f"Optimise ce CV pour {job_target} en {st.session_state['langue']}"}], model="llama3-8b-8192").choices[0].message.content
            st.text_area("CV Amélioré :", res)
            st.download_button("Télécharger CV", res, file_name="cv_zipngo.txt")

    elif menu == "Prospection":
        st.header("🔍 Prospection IA")
        secteur = st.text_input("Secteur d'activité :")
        if st.button("Générer 20 entreprises"):
            # L'IA génère les cibles
            data = client_groq.chat.completions.create(messages=[{"role":"user", "content": f"Liste 20 entreprises en {secteur} avec nom, gérant, ville, pays, email, tel en JSON."}], model="llama3-8b-8192").choices[0].message.content
            st.session_state["leads"] = json.loads(data)
        
        if "leads" in st.session_state:
            st.table(st.session_state["leads"])
            emails = [l['email'] for l in st.session_state["leads"]]
            bcc = ",".join(emails[1:])
            mailto = f"mailto:{emails[0]}?bcc={bcc}&subject=Candidature&body=Bonjour, veuillez trouver mon CV ci-joint."
            st.markdown(f'[📩 Candidater (Ouvrir messagerie)]({mailto})')

    # ... (Ajouter ici le reste de la logique Entretien)
