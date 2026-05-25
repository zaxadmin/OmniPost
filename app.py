import streamlit as st
import json
from groq import Groq
from supabase import create_client
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS International", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- FONCTIONS SYSTÈME ---
def traduire(texte, langue):
    res = client.chat.completions.create(messages=[{"role": "user", "content": f"Traduis en {langue} : {texte}"}], model="llama3-8b-8192")
    return res.choices[0].message.content

def moteur_ia_simple(prompt):
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
    return res.choices[0].message.content

# --- TEXTES & MODES D'EMPLOI ---
TEXTES = {
    "presentation": "Zipngo est une plateforme de recrutement révolutionnaire qui utilise l'IA pour connecter les talents mondiaux avec les entreprises.",
    "candidat_emploi": "MODE D'EMPLOI CANDIDAT : 1. Testez votre CV avec notre simulateur ATS. 2. Lancez une prospection ciblée. 3. Candidatez en 1 clic (Anonymat levé uniquement lors de l'envoi).",
    "employeur_emploi": "MODE D'EMPLOI EMPLOYEUR : 1. Publiez vos offres avec options internationales. 2. Recevez des candidats triés par score d'IA. 3. Utilisez le système de 'Pouce' pour déverrouiller uniquement les profils qui vous intéressent.",
    "cgv": "En utilisant Zipngo, vous acceptez le traitement de vos données par IA et notre politique de confidentialité."
}

# --- NAVIGATION ---
langues = ["Français", "English", "Malagasy", "Español", "Deutsch", "Português", "Italiano", "Nederlands", "Polski", "Русский", "العربية", "中文", "日本語", "한국어", "Türkçe", "हिन्दी", "Tiếng Việt", "ไทย", "Ελληνικά", "Magyar"]
langue = st.sidebar.selectbox("Langue", langues)

# --- CONTACT CRÉATRICE (ENVELOPPE) ---
st.sidebar.markdown("---")
st.sidebar.markdown(f"📧 [Contact Créatrice](mailto:creationsites06@gmail.com)")
st.sidebar.markdown("---")

menu = st.sidebar.radio("Navigation", ["Accueil", "Connexion", "Espace Candidat", "Espace Employeur", "CGV"])

# --- LOGIQUE APP ---
if menu == "Accueil":
    st.title("Zipngo")
    st.write(traduire(TEXTES["presentation"], langue))

elif menu == "Espace Candidat":
    st.header(traduire("Espace Candidat", langue))
    st.info(traduire(TEXTES["candidat_emploi"], langue)) # Mode d'emploi affiché
    
    secteur = st.text_input(traduire("Secteur d'activité", langue))
    if st.button(traduire("Rechercher", langue)):
        st.session_state.cibles = [{"nom": "Entreprise A", "email": "contact@a.com"}, {"nom": "Entreprise B", "email": "contact@b.com"}]
    
    if "cibles" in st.session_state:
        emails = [c['email'] for c in st.session_state.cibles]
        lien = f"mailto:{emails[0]}?bcc={','.join(emails[1:])}&subject=Candidature"
        if st.button(traduire("CANDIDATER (Anonymat levé)", langue)):
            st.markdown(f'<a href="{lien}">{traduire("Ouvrir ma messagerie", langue)}</a>', unsafe_allow_html=True)

elif menu == "Espace Employeur":
    st.header(traduire("Espace Employeur", langue))
    st.info(traduire(TEXTES["employeur_emploi"], langue)) # Mode d'emploi affiché
    
    pays = st.selectbox(traduire("Pays de destination", langue), ["France", "USA", "UK", "Canada", "Madagascar", "Autre"])
    is_remote = st.checkbox(traduire("Poste en 100% Remote", langue))
    if pays:
        reco = moteur_ia_simple(f"Suggère 3 sites d'emploi pour recruter en {pays}")
        st.info(f"{traduire('Sites recommandés', langue)} : {reco}")
        if is_remote: st.success(traduire("Mode REMOTE activé : diffusion globale.", langue))
    
    candidats = [{"id": 1, "nom": "Jean", "score": 95}]
    for c in candidats:
        st.write(f"{c['nom']} - Score: {c['score']}%")
        col1, col2 = st.columns(2)
        if col1.button("👍", key=f"up_{c['id']}"): st.success(traduire("Profil déverrouillé.", langue))
        if col2.button("👎", key=f"down_{c['id']}"): st.error(traduire("Candidature écartée.", langue))

elif menu == "CGV":
    st.write(traduire(TEXTES["cgv"], langue))

elif menu == "Connexion":
    st.header(traduire("Connexion / Création", langue))
    if st.text_input("Email"):
        if st.button(traduire("Envoyer Magik Link", langue)): st.info("Lien envoyé !")
