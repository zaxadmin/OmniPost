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
    3. **Non-garantie :** Outil d'aide à la décision ; aucune garantie de résultat.
    4. **Responsabilité :** L'utilisateur est seul responsable de ses usages.
    5. **Propriété Intellectuelle :** Propriété exclusive de zaxx.app.
    6. **Données :** Collecte minimale. Aucune revente à des tiers.
    7. **Litiges :** Droit français, tribunaux du siège social de zaxx.app.
    """)

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app</h1>", unsafe_allow_html=True)

# Navigation : Tout est accessible pour tes tests
tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.markdown("""
    ### Bienvenue sur **zipngo**
    Nous transformons la complexité du marché de l'emploi en opportunités concrètes. 
    Que vous cherchiez à décrocher le poste de vos rêves ou à bâtir une équipe d'exception, 
    nous vous offrons les outils pour gagner en efficacité et en clarté.
    * **Pour les Talents :** Valorisation sur-mesure de votre parcours.
    * **Pour les Recruteurs :** Gestion sereine et tri intelligent des profils.
    """)
    st.warning("🛠️ **Mode Test :** Accès total à toutes les fonctionnalités.")

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

with tab_employeur:
    st.header("Interface Employeur")
    st.write("Outils de tri et gestion activés.")

# --- FOOTER ---
st.markdown("---")

# Section CGV (Ancre)
st.markdown("<div id='cgv-section'></div>", unsafe_allow_html=True)
with st.expander("📜 Lire les Conditions Générales de Vente"):
    afficher_cgv()

# Footer propre et natif
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>© 2026 zipngo.zaxx.app | <a href='#cgv-section'>Voir les CGV</a></div>", 
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align: center;'>Créatrice : Liliane RAKOTOBE | <a href='mailto:creationsites06@gmail.com'>📧</a></div>", 
    unsafe_allow_html=True
)
