import streamlit as st
import datetime
import re
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- FONCTIONS ---
def creer_pdf_cv_pro(texte_ia, nom_fichier, style):
    pdf = FPDF()
    pdf.add_page()
    if style == "Classique": pdf.set_font("Times", 'B', 16)
    elif style == "Moderne": pdf.set_font("Arial", 'B', 18)
    else: pdf.set_font("Courier", 'B', 16)
    pdf.cell(200, 10, txt="Mon CV Optimisé", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 7, txt=texte_ia)
    pdf.output(nom_fichier)

def afficher_cgv():
    st.markdown("### 📜 CGV (Conditions Générales de Vente)\n1. Accès Candidat 6€/3mois | Recruteur 39€/mois.\n2. Limites Gratuit : 1 CV/mois, 1 campagne/mois.\n3. Premium : 3 CVs/semaine, 20 mails/jour.")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#333333; font-size: 14px; margin-top: 0px;'>.zaxx.app</p>", unsafe_allow_html=True)

# SÉLECTION DE LANGUE
langues = [
    "Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", 
    "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", 
    "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", 
    "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"
]
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue / Select your language", langues, index=0)

# TEXTE DE PRÉSENTATION NEUTRE
st.markdown("""
<div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #4169E1; margin: 20px 0;'>
    <h4 style='margin-top:0;'>Bienvenue sur zipngo</h4>
    L'écosystème intelligent dédié à votre dynamique professionnelle. Que vous soyez en quête de nouvelles opportunités ou en phase de gestion de talents, 
    zipngo agit comme un facilitateur technologique. Nous simplifions la mise en relation et la gestion des parcours.
    <br><br>
    <ul>
        <li><b>Optimisation :</b> Des outils de précision pour valoriser les compétences.</li>
        <li><b>Organisation :</b> Centralisez vos démarches dans un espace sécurisé.</li>
        <li><b>Efficacité :</b> Automatisation des tâches et analyse intelligente des données.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.write("---")
    with st.expander("📜 Lire les CGV"): afficher_cgv()
    st.checkbox("J'accepte les CGV", key="accept_cgv")
    st.markdown("<div style='text-align: center; margin-top: 50px;'>© 2026 zipngo.zaxx.app | <strong>Créatrice : Liliane RAKOTOBE</strong></div>", unsafe_allow_html=True)

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[0]:
        st.subheader("📊 Mon Statut & Historique")
        try:
            historique = supabase.table("candidatures").select("*").order("date", desc=True).execute().data
            for c in historique:
                st.write(f"📅 {c.get('date')} | **{c.get('entreprise')}** - Statut: {c.get('statut')}")
        except: st.info("Aucun historique trouvé.")

    with dossiers[1]:
        st.subheader("📅 Mes Entretiens")
        if 'pouce_actif' not in st.session_state: st.session_state.pouce_actif = False
        if st.button("👍" if st.session_state.pouce_actif else "🤍"):
            st.session_state.pouce_actif = not st.session_state.pouce_actif
            st.rerun()

    with dossiers[3]:
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            if st.button("🔍 Scanner et Analyser le CV"):
                with st.spinner("Analyse ATS en cours..."):
                    reader = PdfReader(up)
                    text = "".join([p.extract_text() for p in reader.pages])
                    res = client.chat.completions.create(messages=[{"role": "user", "content": f"Analyse ATS : {text}"}], model="llama-3.3-70b-versatile")
                    st.session_state.analyse_cv = res.choices[0].message.content
                    st.session_state.texte_original = text
            if 'analyse_cv' in st.session_state:
                st.info(st.session_state.analyse_cv)
                contenu_pro = st.text_area("Optimisation du contenu", value=st.session_state.texte_original, height=300)
                if st.button("✨ Générer version ATS optimisée"):
                    res_opt = client.chat.completions.create(messages=[{"role": "user", "content": f"Optimise pour ATS : {contenu_pro}"}], model="llama-3.3-70b-versatile")
                    st.session_state.texte_final = res_opt.choices[0].message.content
                    st.success("Contenu optimisé prêt !")
                if 'texte_final' in st.session_state:
                    style = st.selectbox("Style de mise en page", ["Classique", "Moderne", "Minimaliste"])
                    if st.button("🚀 Générer et Archiver le CV"):
                        nom_f = f"CV_Optimise_{datetime.date.today()}.pdf"
                        creer_pdf_cv_pro(st.session_state.texte_final, nom_f, style)
                        supabase.table("cvs").insert({"nom_fichier": nom_f, "contenu": st.session_state.texte_final}).execute()
                        st.success(f"✅ {nom_f} archivé !")

    with dossiers[4]:
        st.subheader("🌐 Prospection Spontanée")
        domaines = ["Restauration", "Hôtellerie", "Commerce", "Santé", "BTP", "Logistique", "Informatique", "Immobilier", "Événementiel", "Conseil", "Industrie", "Agriculture", "Éducation", "Culture", "Services", "Tourisme", "Artisanat", "Transport", "Finance", "Administration"]
        categorie = st.selectbox("Domaine d'activité", domaines)
        ville = st.text_input("Ville")
        
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            with st.spinner("Recherche..."):
                liste_exclue = [c['email_destinataire'] for c in supabase.table("sourcing").select("email_destinataire").execute().data]
                prompt = f"Expert sourcing, trouve 20 emails officiels pour '{categorie}' à '{ville}'. Exclus : {', '.join(liste_exclue)}. Liste uniquement, un par ligne."
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.emails_trouves = res.choices[0].message.content

        if 'emails_trouves' in st.session_state:
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', st.session_state.emails_trouves)
            dest = st.text_input("Destinataire principal", value=emails[0] if emails else "")
            
            # Correction ici : Utilisation des triples guillemets pour le message
            msg = st.text_area("Message", value="""Madame, Monsieur, 

Je me permets de vous adresser ma candidature spontanée pour rejoindre votre entreprise. Je suis convaincu que mon profil pourrait répondre à vos besoins actuels ou futurs.
Je vous prie d'agréer mes salutations distinguées. Ci-joint mon curriculum vitae.

Cordialement,""", height=250)
            
            mode_cv = st.radio("Source du CV", ["Choisir dans l'App", "Uploader CV"])
            cv_f = None
            if mode_cv == "Choisir dans l'App":
                data = supabase.table("cvs").select("nom_fichier").execute().data
                cv_f = st.selectbox("Mes CVs", [c['nom_fichier'] for c in data])
            else:
                cv_f = st.file_uploader("Upload CV", type=["pdf"])

            if st.button("🚀 Valider et Envoyer"):
                try:
                    content = cv_f.read() if hasattr(cv_f, 'read') else open(cv_f, "rb").read()
                    resend.Emails.send({"from": "contact@zaxx.app", "to": dest, "bcc": emails[1:20], "subject": "Candidature spontanée", "text": msg, "attachments": [{"filename": "CV.pdf", "content": list(content)}]})
                    for e in emails: supabase.table("sourcing").insert({"email_destinataire": e, "objet": "Candidature", "message": msg, "date": str(datetime.date.today())}).execute()
                    supabase.table("candidatures").insert({"type": "Spontanée", "entreprise": categorie, "date": str(datetime.date.today()), "statut": "ENVOYÉ"}).execute()
                    st.success("✅ Candidatures envoyées et archivées !")
                except Exception as e: st.error(f"Erreur : {e}")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
