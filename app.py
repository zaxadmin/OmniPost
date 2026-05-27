import streamlit as st
import datetime
import re  # Import nécessaire pour le nettoyage des emails
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
        rayon = st.slider("Rayon de recherche (km)", 0, 100, 50)
        
        if st.button("🔍 Rechercher 20 contacts"):
            with st.spinner("Recherche en cours..."):
                prompt = f"Trouve 20 emails officiels pour '{secteur}' à '{ville}'. Donne uniquement la liste des emails, un par ligne, rien d'autre."
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.session_state.emails_trouves = res.choices[0].message.content
                st.success("Extraction terminée !")
        
        if 'emails_trouves' in st.session_state:
            # Extraction propre des emails via Regex
            emails_bruts = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', st.session_state.emails_trouves)
            
            dest = st.text_input("Destinataire principal", value=emails_bruts[0] if emails_bruts else "")
            cc = st.text_area("19 emails en copie cachée (séparés par des virgules)", value=", ".join(emails_bruts[1:20]) if len(emails_bruts) > 1 else "")
            
            corps_lettre = "Madame, Monsieur,\n\nJe me permets de vous soumettre ma candidature..."
            obj = st.text_input("Objet", value=f"Candidature au poste de {secteur}")
            msg = st.text_area("Message", value=corps_lettre, height=250)
            
            # --- BLOC ROBUSTE CVS ---
            try:
                response = supabase.table("cvs").select("nom_fichier").execute()
                cvs = response.data
                if cvs and len(cvs) > 0:
                    nom_cv = st.selectbox("Attacher mon CV", [c['nom_fichier'] for c in cvs])
                else:
                    st.warning("⚠️ Aucun CV trouvé. Chargez un CV dans 'Relooking' avant.")
            except Exception:
                st.warning("Erreur de lecture des CVs.")
            
            if st.button("🚀 Valider et Envoyer"):
                try:
                    supabase.table("sourcing").insert({
                        "email_destinataire": dest, "objet": obj, "message": msg, "date": str(datetime.date.today())
                    }).execute()
                    supabase.table("candidatures").insert({
                        "type": "Spontanée", "entreprise": f"{secteur} ({ville} +{rayon}km)", "date": str(datetime.date.today()), "statut": "ENVOYÉ"
                    }).execute()
                    st.success("✅ Campagne enregistrée avec succès !")
                except Exception as e:
                    st.error(f"Erreur d'insertion : {e}")

    with dossiers[3]: # ✨ Relooking
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            if st.button("🚀 Produire et Enregistrer"):
                try:
                    reader = PdfReader(up)
                    text = "".join([p.extract_text() for p in reader.pages])
                    supabase.table("cvs").insert({"nom_fichier": up.name, "contenu": text}).execute()
                    st.success("✅ CV produit et enregistré !")
                except Exception as e:
                    st.error(f"Erreur : {e}")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
