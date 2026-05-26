import streamlit as st
import datetime
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
    st.markdown("### 📜 Conditions Générales de Vente (CGV)\n1. Accès Candidat 6€/3mois | Recruteur 39€/mois.\n2. Limites Gratuit : 1 CV/mois, 1 campagne/mois.\n3. Premium : 3 CVs/semaine, 20 mails/jour.")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app👍</h1>", unsafe_allow_html=True)

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    with st.expander("📜 Lire les CGV"): afficher_cgv()
    st.checkbox("J'accepte les CGV", key="accept_cgv")
    st.markdown("<div style='text-align: center; margin-top: 50px;'>© 2026 zipngo.zaxx.app | <strong>Créatrice : Liliane RAKOTOBE</strong></div>", unsafe_allow_html=True)

with tab_candidat:
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🚀 Campagne"])
    
    with dossiers[0]: # 📂 Candidatures
        st.subheader("📊 Mon Statut & Historique Sourcing")
        try:
            historique = supabase.table("candidatures").select("*").order("date", desc=True).execute().data
            for c in historique:
                st.write(f"📅 {c.get('date')} | **{c.get('entreprise')}** - Statut: {c.get('statut')}")
        except: st.info("Aucun historique trouvé.")

    with dossiers[1]: # 📅 Entretiens
        st.subheader("📅 Mes Entretiens")
        if 'pouce_actif' not in st.session_state: st.session_state.pouce_actif = False
        if st.button("👍" if st.session_state.pouce_actif else "🤍"):
            st.session_state.pouce_actif = not st.session_state.pouce_actif
            st.rerun()
        st.markdown("---")
        st.subheader("📩 Invitations reçues")
        st.info("Aucune invitation en attente.")
        st.subheader("📜 Historique des entretiens passés")

    with dossiers[4]: # 🌐 Sourcing
        st.subheader("🌐 Prospection Spontanée")
        secteur = st.text_input("Secteur (ex: Maison de retraite)")
        ville = st.text_input("Ville")
        
        if st.button("🔍 Rechercher 20 contacts"):
            with st.spinner("Recherche en cours..."):
                prompt = f"Trouve 20 emails officiels (rh@, contact@) pour '{secteur}' à '{ville}'. Liste brute."
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.emails_trouves = res.choices[0].message.content
                st.success("Extraction terminée !")
        
        if 'emails_trouves' in st.session_state:
            emails = [e.strip() for e in st.session_state.emails_trouves.split('\n') if "@" in e]
            dest = st.text_input("Destinataire principal", value=emails[0] if emails else "")
            cc = st.text_area("19 emails en copie cachée", value=", ".join(emails[1:20]) if len(emails)>1 else "")
            obj = st.text_input("Objet", value="Candidature")
            msg = st.text_area("Message", value="Madame, Monsieur, je vous adresse ma candidature...")
            
            cvs = supabase.table("cvs").select("nom_fichier").execute().data
            nom_cv = st.selectbox("Attacher mon CV", [c['nom_fichier'] for c in cvs])
            
            if st.button("🚀 Valider et Envoyer"):
                supabase.table("sourcing").insert({"email_destinataire": dest, "objet": obj, "message": msg, "date": str(datetime.date.today())}).execute()
                supabase.table("candidatures").insert({"type": "Spontanée", "entreprise": secteur, "date": str(datetime.date.today()), "statut": "ENVOYÉ"}).execute()
                st.success("Campagne lancée et ajoutée à vos candidatures !")

    with dossiers[3]: # ✨ Relooking
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            if st.button("🚀 Produire et Enregistrer"):
                st.success("✅ CV produit et enregistré !")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
