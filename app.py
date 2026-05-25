import streamlit as st
import json
import re
from groq import Groq
from supabase import create_client
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- FONCTIONS SYSTÈME ---
def est_email_valide(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def traduire(texte, langue):
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": f"Traduis en {langue} : {texte}"}], model="llama3-8b-8192")
        return res.choices[0].message.content
    except:
        return texte

def moteur_ia(prompt):
    try:
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
        return res.choices[0].message.content
    except:
        return "Service IA temporairement indisponible."

# --- LOGIQUE JITSI ---
def creer_salle_jitsi(id_candidature):
    return f"https://meet.jit.si/zipngo-{id_candidature}"

# --- TEXTES & CGV ---
TEXTES = {
    "presentation": "Zipngo est une plateforme de recrutement révolutionnaire qui utilise l'IA pour connecter les talents mondiaux avec les entreprises.",
    "candidat_emploi": "MODE D'EMPLOI CANDIDAT : 1. Testez votre CV avec notre ATS. 2. Prospection (20/mois). 3. Entretien visio Jitsi.",
    "employeur_emploi": "MODE D'EMPLOI EMPLOYEUR : 1. Publiez vos offres (3/mois). 2. Recevez des candidats triés par IA. 3. Utilisez le 'Pouce' pour déverrouiller et initier la visio.",
    "cgv": """**CGV & RESPONSABILITÉ :**
    - **Non-Responsabilité :** Zipngo est un outil de mise en relation. Nous déclinons toute responsabilité sur la véracité des informations (CV/Offres). Chaque utilisateur est seul responsable de ses publications.
    - **Politique Freemium :** Après 3 mois de test, le profil gratuit passe en 'Veille'. Réactivation immédiate dès souscription Premium.
    - **Suppression :** Suppression totale sur simple demande à creationsites06@gmail.com.
    - **Limites :** Candidats (20 prospections, 1 analyse/mois) | Employeurs (1 recherche, 3 offres/mois)."""
}

# --- NAVIGATION & RÔLE AVEC VALIDATION CGV ---
if "role" not in st.session_state:
    st.sidebar.title("Connexion / Création")
    st.session_state.role = st.sidebar.radio("Je suis un :", ["Candidat", "Employeur"])
    email = st.sidebar.text_input("Votre Email")
    accept_cgv = st.sidebar.checkbox("J'accepte les CGV et le traitement de mes données par IA.")
    if st.sidebar.button("Envoyer Magik Link"):
        if not email: st.sidebar.error("Veuillez entrer votre email.")
        elif not accept_cgv: st.sidebar.error("Vous devez accepter les CGV.")
        else: st.sidebar.info("Lien envoyé ! Vérifiez vos spams.")
    st.stop()

# Initialisation de l'état pour les créneaux
if "creneaux_proposes" not in st.session_state: st.session_state.creneaux_proposes = []

langues = ["Français", "English", "Malagasy", "Español", "Deutsch", "Português", "Italiano", "Nederlands", "Polski", "Русский", "العربية", "中文", "日本語", "한국어", "Türkçe", "हिन्दी", "Tiếng Việt", "ไทย", "Ελληνικά", "Magyar"]
langue = st.sidebar.selectbox("Langue", langues)

# --- SIDEBAR PREMIUM & CONTACT ---
st.sidebar.markdown("---")
prix = "6€" if st.session_state.role == "Candidat" else "39€"
if st.sidebar.button(f"🚀 Passer Premium ({prix} / 3 mois)"): st.sidebar.success("Redirection vers Stripe...")
st.sidebar.markdown(f"📧 [Contact Créatrice](mailto:creationsites06@gmail.com)")

menu = st.sidebar.radio("Navigation", ["Accueil", "Espace de Travail", "CGV"])

# --- LOGIQUE APP ---
if menu == "Accueil":
    st.title("Zipngo")
    st.write(traduire(TEXTES["presentation"], langue))

elif menu == "Espace de Travail":
    if st.session_state.role == "Candidat":
        st.header(traduire("Espace Candidat", langue))
        st.info(traduire(TEXTES["candidat_emploi"], langue))
        
        if st.session_state.creneaux_proposes:
            st.subheader("Choisir mon créneau")
            choix = st.selectbox("Horaires proposés par l'employeur :", st.session_state.creneaux_proposes)
            if st.button("Confirmer mon créneau"):
                st.warning(f"Entretien validé : [Rejoindre la salle Jitsi]({creer_salle_jitsi('1')})")
        
        secteur = st.text_input(traduire("Secteur d'activité", langue))
        if st.button(traduire("Lancer 20 prospections", langue)): st.success("Prospection effectuée.")
    
    else: # Employeur
        st.header(traduire("Espace Employeur", langue))
        st.info(traduire(TEXTES["employeur_emploi"], langue))
        
        # Gestion des créneaux
        st.subheader("Définir mes disponibilités")
        dispos = ["10:00", "11:00", "14:00", "15:00", "16:00"]
        st.session_state.creneaux_proposes = st.multiselect("Sélectionnez vos créneaux ouverts :", dispos)
        
        pays = st.selectbox("Pays", ["France", "USA", "UK", "Canada", "Madagascar", "Autre"])
        if st.button("Rechercher un candidat"):
            reco = moteur_ia(f"Suggère 3 sites d'emploi pour recruter en {pays}")
            st.info(f"{traduire('Sites recommandés', langue)} : {reco}")
            st.write("Résultat : Jean (Score 95%)")
            if st.button("👍 Déverrouiller"):
                st.success("Candidat déverrouillé. Il pourra maintenant choisir parmi vos créneaux.")

elif menu == "CGV":
    st.markdown(TEXTES["cgv"])
    if st.button("Demander la suppression de mon compte"):
        st.warning("Veuillez envoyer un mail à creationsites06@gmail.com pour effacer vos données.")
