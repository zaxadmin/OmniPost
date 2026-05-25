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

def scrapper_cibles(secteur):
    prompt = f"Génère une liste de 3 entreprises actives dans le secteur '{secteur}' avec leur email de contact RH et un nom de responsable. Format : Nom|Email|Responsable"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
    return res.choices[0].message.content.split('\n')

def creer_salle_jitsi(id_candidature):
    return f"https://meet.jit.si/zipngo-{id_candidature}"

# --- TEXTES & CGV ---
TEXTES = {
    "presentation": "### 🚀 Bienvenue sur Zipngo, la nouvelle ère du recrutement international.\n\nZipngo n'est pas seulement une plateforme de mise en relation, c'est **votre accélérateur de carrière et de croissance**. Nous utilisons l'IA pour connecter les talents mondiaux aux entreprises ambitieuses.",
    "candidat_emploi": "MODE D'EMPLOI CANDIDAT : 1. Testez votre CV avec notre ATS. 2. Prospection (20/mois). 3. Entretien visio Jitsi.",
    "employeur_emploi": "MODE D'EMPLOI EMPLOYEUR : 1. Publiez vos offres (3/mois). 2. Recevez des candidats triés par IA. 3. Utilisez le 'Pouce' pour déverrouiller et initier la visio.",
    "cgv": """**CGV & RESPONSABILITÉ :**
    - **Non-Responsabilité :** Zipngo est un outil de mise en relation. Chaque utilisateur est seul responsable de ses publications.
    - **Politique Freemium :** Après 3 mois de test, le profil gratuit passe en 'Veille'. Réactivation immédiate dès souscription Premium.
    - **Suppression :** Suppression totale sur simple demande à creationsites06@gmail.com.
    - **Limites :** Candidats (20 prospections, 1 analyse/mois) | Employeurs (1 recherche, 3 offres/mois)."""
}

# --- NAVIGATION & RÔLE ---
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

# Initialisation état
if "creneaux_proposes" not in st.session_state: st.session_state.creneaux_proposes = []
if "cibles_trouvees" not in st.session_state: st.session_state.cibles_trouvees = []

langue = st.sidebar.selectbox("Langue", ["Français", "English", "Malagasy", "Español", "Deutsch", "Português", "Italiano", "Nederlands", "Polski", "Русский", "العربية", "中文", "日本語", "한국어", "Türkçe", "हिन्दी", "Tiếng Việt", "ไทย", "Ελληνικά", "Magyar"])

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
        st.header("Espace Candidat")
        tab1, tab2, tab3, tab4 = st.tabs(["Candidater (Scrapping)", "Mes Candidatures", "Mes CVs", "Mes Entretiens"])
        with tab1:
            secteur = st.text_input("Secteur visé (ex: Data Science)")
            if st.button("Identifier des cibles"):
                st.session_state.cibles_trouvees = scrapper_cibles(secteur)
            for ligne in st.session_state.cibles_trouvees:
                if "|" in ligne:
                    nom, email, resp = ligne.split('|')
                    st.write(f"🏢 **{nom}** (Contact: {resp})")
                    st.link_button("Envoyer candidature spontanée", f"mailto:{email}")
        with tab2: st.write("Suivi de vos envois...")
        with tab3:
            st.file_uploader("Upload mon CV", type=['pdf', 'docx'])
            st.download_button("Télécharger mon CV actuel", "data", "mon_cv.pdf")
        with tab4:
            if st.session_state.creneaux_proposes:
                choix = st.selectbox("Choisir mon créneau", st.session_state.creneaux_proposes)
                if st.button("Confirmer entretien"): st.warning(f"Lien : [Rejoindre Jitsi]({creer_salle_jitsi('1')})")
            st.subheader("Historique des entretiens")
            st.write("• Entreprise A (05/05) : Profil retenu.")

    else: # Employeur
        st.header("Espace Employeur")
        tab1, tab2, tab3 = st.tabs(["Poster une offre (1 clic)", "Programmer entretiens", "Talents (CVs triés)"])
        with tab1: st.button("Publier offre en 1 clic")
        with tab2:
            st.session_state.creneaux_proposes = st.multiselect("Disponibilités", ["10:00", "14:00", "16:00"])
            st.subheader("Suivi des entretiens")
            st.write("• Jean (10/05) : Très bon profil.")
            st.text_area("Ajouter un compte-rendu")
        with tab3:
            pays = st.selectbox("Pays", ["France", "USA", "UK", "Canada", "Madagascar", "Autre"])
            if st.button("Rechercher un candidat"):
                reco = moteur_ia(f"Suggère 3 profils candidats pour recruter en {pays}")
                st.info(f"Talents détectés : {reco}")
                if st.button("👍 Déverrouiller ce talent"): st.success("Candidat dispatché.")

elif menu == "CGV":
    st.markdown(TEXTES["cgv"])
    if st.button("Demander la suppression de mon compte"): st.warning("Envoyez un mail à creationsites06@gmail.com.")
