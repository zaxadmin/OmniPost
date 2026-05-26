import streamlit as st
import requests
import base64
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
    st.markdown("""
    ### 📜 Conditions Générales de Vente (CGV)
    1. **Objet :** Services d'optimisation de carrière (zipngo).
    2. **Tarifs :** Candidat 6€/3mois | Recruteur 39€/mois.
    3. **Gestion profil :** Accès actif 3 mois, puis mise en veille automatique.
    4. **Limites Gratuit :** 1 CV optimisé/mois, 1 campagne/mois.
    5. **Données :** Collecte minimale. Aucune revente à des tiers.
    """)

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app</h1>", unsafe_allow_html=True)

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    ### Bienvenue sur **zipngo**
    **zipngo** est un écosystème conçu pour maximiser votre impact professionnel, que vous soyez un talent en quête d'opportunités ou un recruteur à la recherche de la perle rare.

    ---
    #### 🟢 Accès Gratuit
    * **Optimisation de CV :** 1 CV par mois.
    * **Campagne :** 1 campagne par mois.
    * **Durée de vie :** Profil actif pendant 3 mois, puis mise en veille automatique.
    * **Outils :** Accès aux outils de diagnostic et de gestion des entretiens.
    """)
    
    if st.button("Tester gratuitement"):
        # Note : Si tu n'as pas de dossiers 'pages/', utilise ceci pour naviguer :
        st.session_state.active_tab = "🚀 Candidat"
        st.rerun()

    st.markdown("""
    ---
    #### 💎 Pourquoi passer en mode Premium ?
    *Débloquez une puissance de frappe supérieure pour vos candidatures :*
    * **CVs optimisés :** Jusqu'à 3 CVs par semaine.
    * **Campagnes de contact :** Jusqu'à 20 emails par jour.
    * **Priorité :** Accès illimité à nos outils d'optimisation les plus poussés.
    * **Avantage exclusif :** Accès en avant-première à toutes les nouvelles fonctionnalités.
    """)
    
    if st.button("🚀 Booster ma carrière avec le Premium"):
        st.info("Redirection vers la page de paiement...")

    st.info("💡 **Mode Test :** Accès total actuel pour découvrir nos fonctionnalités.")

with tab_candidat:
    st.header("Mon Espace Candidat")
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🚀 Campagne"])
    
    with dossiers[1]: # Entretiens
        st.subheader("📅 Mes Entretiens")
        # ... (reste de ton code inchangé)

    with dossiers[2]: # CVs
        # ... (reste de ton code inchangé)

    with dossiers[3]: # Relooking
        # ... (reste de ton code inchangé)

# --- FOOTER ---
st.markdown("---")
# ... (fin du fichier)
