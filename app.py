import streamlit as st
import datetime
import re
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- INITIALISATION NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 0

# Liste des sections (Campagne supprimée)
pages = ["🏠 Accueil", "📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"]

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app👍</h1>", unsafe_allow_html=True)

# --- BOUTONS NAVIGATION ---
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    if st.button("⬅️ Précédent") and st.session_state.page > 0:
        st.session_state.page -= 1
        st.rerun()
with col3:
    if st.button("Suivant ➡️") and st.session_state.page < len(pages) - 1:
        st.session_state.page += 1
        st.rerun()

st.write(f"### {pages[st.session_state.page]}")
st.divider()

# --- LOGIQUE DES PAGES ---
# Page 0 : Accueil
if st.session_state.page == 0:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.checkbox("J'accepte les CGV", key="accept_cgv")

# Page 1 : Candidatures
elif st.session_state.page == 1:
    st.subheader("📊 Mon Statut & Historique Sourcing")
    try:
        historique = supabase.table("candidatures").select("*").order("date", desc=True).execute().data
        for c in historique:
            st.write(f"📅 {c.get('date')} | **{c.get('entreprise')}** - Statut: {c.get('statut')}")
    except: st.info("Aucun historique trouvé.")

# Page 2 : Entretiens
elif st.session_state.page == 2:
    st.subheader("📅 Mes Entretiens")
    if st.button("🤍"): st.rerun()

# Page 4 : Relooking CV
elif st.session_state.page == 4:
    st.subheader("✨ Relooking & Analyse ATS")
    up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
    if up and st.button("🚀 Produire et Enregistrer"):
        try:
            reader = PdfReader(up)
            text = "".join([p.extract_text() for p in reader.pages])
            supabase.table("cvs").insert({"nom_fichier": up.name, "contenu": text}).execute()
            st.success("✅ CV enregistré !")
        except Exception as e: st.error(f"Erreur : {e}")

# Page 5 : Sourcing
elif st.session_state.page == 5:
    st.subheader("🌐 Prospection Spontanée")
    secteur = st.text_input("Secteur visé")
    ville = st.text_input("Ville")
    
    if st.button("🔍 Rechercher 20 contacts"):
        with st.spinner("Recherche..."):
            prompt = f"Trouve 20 emails officiels pour '{secteur}' à '{ville}'. Donne uniquement la liste des emails, un par ligne."
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
            st.session_state.emails_trouves = res.choices[0].message.content
            st.success("Extraction terminée !")
    
    if 'emails_trouves' in st.session_state:
        emails_bruts = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', st.session_state.emails_trouves)
        dest = st.text_input("Destinataire principal", value=emails_bruts[0] if emails_bruts else "")
        cc = st.text_area("19 emails en copie cachée", value=", ".join(emails_bruts[1:20]) if len(emails_bruts) > 1 else "")
        msg = st.text_area("Message", value="""Madame, Monsieur,\n\nJe me permets de vous soumettre spontanément ma candidature. Très motivé à l'idée de rejoindre votre équipe, je suis convaincu que mon profil correspond aux attentes de votre entreprise.\n\nVous trouverez en pièce jointe mon curriculum vitae, qui détaille mon expérience et mes compétences. Je reste à votre entière disposition pour convenir d'un entretien afin de vous exposer plus en détail mes motivations.\n\nDans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.\n\nCordialement,\n[Ton Prénom] [Ton Nom]\n[Ton numéro de téléphone]""", height=250)
        
        choix_cv = st.radio("CV à joindre :", ["Choisir depuis la base", "Uploader un fichier"])
        cv_final = None
        if choix_cv == "Choisir depuis la base":
            data = supabase.table("cvs").select("nom_fichier").execute().data
            if data: cv_final = st.selectbox("Mes CVs", [c['nom_fichier'] for c in data])
        else:
            up_local = st.file_uploader("Upload local", type=["pdf"])
            if up_local: cv_final = up_local.name
        
        if st.button("🚀 Valider et Envoyer"):
            if cv_final:
                supabase.table("sourcing").insert({"email_destinataire": dest, "objet": "Candidature spontanée", "message": msg, "date": str(datetime.date.today())}).execute()
                supabase.table("candidatures").insert({"type": "Spontanée", "entreprise": secteur, "date": str(datetime.date.today()), "statut": "ENVOYÉ"}).execute()
                st.success("✅ Candidature envoyée !")
            else: st.error("Sélectionnez un CV.")

# Interface Employeur
st.sidebar.divider()
if st.sidebar.button("💼 Interface Employeur"):
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
