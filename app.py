import streamlit as st
import imaplib
import email
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
SALON_FIXE = "https://meet.jit.si/zipngo-entretien-privé"

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
    2. **Tarifs :** Candidat : 6€/3mois | Recruteur : 39€/mois.
    3. **Non-garantie :** Outil d'aide à la décision ; aucune garantie de résultat.
    4. **Responsabilité :** L'utilisateur est seul responsable de ses usages (RGPD, etc.).
    5. **Propriété Intellectuelle :** Propriété exclusive de zaxx.app.
    6. **Données :** Collecte minimale pour le service. Aucune revente.
    7. **Litiges :** Droit français, tribunaux du siège social de zaxx.app.
    """)

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app</h1>", unsafe_allow_html=True)

# Déconnexion rapide pour tester les profils
if st.sidebar.button("Déconnexion"):
    supabase.auth.sign_out()
    st.rerun()

session = supabase.auth.get_session()

# Navigation dynamique
if not session:
    tab_home = st.tabs(["🏠 Accueil"])[0]
else:
    tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.markdown("""
    Bienvenue sur **zipngo**. Nous transformons la complexité du marché de l'emploi en opportunités concrètes.
    * **Talents :** Valorisation sur-mesure et ciblage direct.
    * **Recruteurs :** Tri intelligent et gestion sereine des flux.
    """)
    st.info("💡 **Mode Test :** Connectez-vous avec vos identifiants (Email + Mot de passe).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Connexion")
        email_test = st.text_input("Email", key="email")
        pass_test = st.text_input("Mot de passe", type="password", key="password")
        if st.button("Se connecter"):
            try:
                supabase.auth.sign_in_with_password({"email": email_test, "password": pass_test})
                st.rerun()
            except Exception:
                st.error("Identifiants incorrects.")

if session:
    with tab_candidat:
        st.header("Mon Espace Candidat")
        dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking IA", "🌐 Sourcing", "🚀 Campagne"])
        
        with dossiers[3]: # Relooking IA
            up = st.file_uploader("Upload mon CV", type=["pdf"])
            poste = st.text_input("Poste visé")
            style = st.selectbox("Style :", ["Classique", "Moderne", "Créatif"])
            if up and poste and st.button("Optimiser"):
                reader = PdfReader(up)
                texte = "".join([p.extract_text() for p in reader.pages])
                res = client.chat.completions.create(messages=[{"role": "user", "content": f"Optimise ce CV pour {poste}: {texte}"}], model="llama-3.3-70b-versatile")
                creer_pdf_cv_pro(res.choices[0].message.content, "cv_opt.pdf", style)
                with open("cv_opt.pdf", "rb") as f: st.download_button("📥 Télécharger", f, "cv_opt.pdf")
        
        with dossiers[4]: # Sourcing
            secteur = st.text_input("Secteur")
            if st.button("Identifier"):
                res = client.chat.completions.create(messages=[{"role": "user", "content": f"20 emails RH en {secteur}."}], model="llama-3.3-70b-versatile")
                st.write(res.choices[0].message.content)
        
        with st.expander("📜 Voir les CGV"):
            afficher_cgv()
            
    with tab_employeur:
        st.header("Interface Employeur")
        st.write("Outils de tri et gestion activés.")
        with st.expander("📜 Voir les CGV"):
            afficher_cgv()
