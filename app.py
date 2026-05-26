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
        col1, col2 = st.columns(2)
        with col1: st.write("🟢 **Accès Gratuit :** 1 campagne/mois.")
        with col2: st.write("💎 **Mode Premium :** 20 mails/jour.")
        st.markdown("---")
        try:
            historique = supabase.table("sourcing").select("*").order("id", desc=True).execute().data
            for h in historique:
                with st.expander(f"📅 {h.get('date')} | Destinataire : {h.get('email_destinataire')}"):
                    st.write(f"**Objet :** {h.get('objet')}")
        except: st.info("Aucun historique trouvé.")

    with dossiers[1]: # 📅 Entretiens
        st.subheader("📅 Mes Entretiens")
        if 'pouce_actif' not in st.session_state: st.session_state.pouce_actif = False
        if st.button("👍" if st.session_state.pouce_actif else "🤍"):
            st.session_state.pouce_actif = not st.session_state.pouce_actif
            st.rerun()
        st.markdown("---")
        st.subheader("📩 Invitations reçues")
        # Logique Jitsi / Validation horaire
        st.info("Aucune invitation en attente.")
        st.subheader("📜 Historique des entretiens passés")

    with dossiers[4]: # 🌐 Sourcing (1 + 19)
        st.subheader("🌐 Prospection Spontanée (Campagne 1+19)")
        destinataire = st.text_input("Destinataire principal")
        copie_cachee = st.text_area("19 emails en copie cachée")
        objet = st.text_input("Objet du mail")
        message = st.text_area("Message")
        if st.button("🚀 Envoyer à 20 contacts"):
            supabase.table("sourcing").insert({"email_destinataire": destinataire, "objet": objet, "message": message, "date": str(datetime.date.today())}).execute()
            st.success("Campagne lancée !")

    with dossiers[3]: # ✨ Relooking
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("Upload votre CV (PDF)", type=["pdf"])
        if up:
            # ... (logique scan ATS + bouton Produire et Enregistrer)
            if st.button("🚀 Produire et Enregistrer"):
                st.success("✅ CV produit et enregistré !")

with tab_employeur:
    st.header("Interface Employeur")
    st.info("Module en cours de déploiement.")
