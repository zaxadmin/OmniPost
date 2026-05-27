import streamlit as st
import datetime
import re
from fpdf import FPDF
from groq import Groq
from supabase import create_client
from PyPDF2 import PdfReader
from postgrest.exceptions import APIError
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- FONCTION DE SÉCURITÉ ---
def safe_supabase_query(operation):
    try:
        return operation.execute()
    except APIError as e:
        st.error(f"Erreur Supabase : {e.message}")
        return None
    except Exception as e:
        st.error(f"Erreur inattendue : {str(e)}")
        return None

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
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing"])
    
    with dossiers[0]: # 📂 Candidatures
        st.subheader("📊 Mon Statut & Historique Sourcing")
        res = safe_supabase_query(supabase.table("candidatures").select("*").order("date", desc=True))
        if res and res.data:
            for c in res.data:
                st.write(f"📅 {c.get('date')} | **{c.get('entreprise')}** - Statut: {c.get('statut')}")
        else: st.info("Aucun historique trouvé.")

    with dossiers[1]: # 📅 Entretiens
        st.subheader("📅 Mes Entretiens")
        if 'pouce_actif' not in st.session_state: st.session_state.pouce_actif = False
        if st.button("👍" if st.session_state.pouce_actif else "🤍"):
            st.session_state.pouce_actif = not st.session_state.pouce_actif
            st.rerun()

    with dossiers[3]: # ✨ Relooking CV
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            if st.button("🔍 Scanner et Analyser le CV"):
                with st.spinner("Analyse ATS en cours..."):
                    reader = PdfReader(up)
                    text = "".join([p.extract_text() for p in reader.pages])
                    res = client.chat.completions.create(messages=[{"role": "user", "content": f"Analyse ce CV : {text}"}], model="llama-3.3-70b-versatile")
                    st.session_state.analyse_cv = res.choices[0].message.content
                    st.session_state.texte_original = text
            
            if 'analyse_cv' in st.session_state:
                st.info(st.session_state.analyse_cv)
                contenu_pro = st.text_area("Optimisation", value=st.session_state.texte_original, height=300)
                if st.button("✨ Générer version ATS optimisée"):
                    res_opt = client.chat.completions.create(messages=[{"role": "user", "content": f"Optimise pour ATS : {contenu_pro}"}], model="llama-3.3-70b-versatile")
                    st.session_state.texte_final = res_opt.choices[0].message.content
                    st.success("Contenu optimisé !")

            if 'texte_final' in st.session_state:
                style = st.selectbox("Style", ["Classique", "Moderne", "Minimaliste"])
                if st.button("🚀 Générer et Archiver le CV"):
                    nom_f = f"CV_Optimise_{datetime.date.today()}.pdf"
                    creer_pdf_cv_pro(st.session_state.texte_final, nom_f, style)
                    safe_supabase_query(supabase.table("cvs").insert({"nom_fichier": nom_f, "contenu": st.session_state.texte_final}))
                    st.success("✅ Archivé !")

    with dossiers[4]: # 🌐 Sourcing
        st.subheader("🌐 Prospection Spontanée")
        domaines = ["Restauration", "Hôtellerie", "Commerce", "Santé", "BTP", "Logistique", "Informatique", "Immobilier"]
        categorie = st.selectbox("Domaine", domaines)
        ville = st.text_input("Ville")
        
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            with st.spinner("Recherche..."):
                deja = safe_supabase_query(supabase.table("sourcing").select("email_destinataire").eq("entreprise", categorie))
                exclus = [c['email_destinataire'] for c in deja.data] if deja else []
                prompt = f"Trouve 20 emails officiels pour '{categorie}' à '{ville}'. Exclus : {', '.join(exclus)}. Liste uniquement."
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.emails_trouves = res.choices[0].message.content

        if 'emails_trouves' in st.session_state:
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', st.session_state.emails_trouves)
            dest = st.text_input("Destinataire principal", value=emails[0] if emails else "")
            msg = st.text_area("Message", value="Madame, Monsieur, je me permets de vous adresser ma candidature spontanée...", height=200)
            
            cv_db = safe_supabase_query(supabase.table("cvs").select("nom_fichier"))
            cv_final = st.selectbox("Choisir CV à envoyer", [c['nom_fichier'] for c in cv_db.data] if cv_db else [])
            
            if st.button("🚀 Envoyer par Resend (avec PDF)"):
                try:
                    with open(cv_final, "rb") as f: file_c = f.read()
                    resend.Emails.send({
                        "from": "contact@zaxx.app", "to": dest, "bcc": emails[1:],
                        "subject": "Candidature spontanée", "text": msg,
                        "attachments": [{"filename": cv_final, "content": list(file_c)}]
                    })
                    for email in emails:
                        safe_supabase_query(supabase.table("sourcing").insert({"email_destinataire": email, "entreprise": categorie, "date": str(datetime.date.today())}))
                    st.success("✅ Candidatures envoyées !")
                except Exception as e: st.error(f"Erreur : {e}")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
