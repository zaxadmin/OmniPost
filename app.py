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
    3. **Non-garantie :** Outil d'aide à la décision.
    4. **Responsabilité :** L'utilisateur est seul responsable de ses usages.
    5. **Propriété Intellectuelle :** Propriété exclusive de zaxx.app.
    6. **Données :** Collecte minimale. Aucune revente à des tiers.
    7. **Litiges :** Droit français, tribunaux du siège social de zaxx.app.
    """)

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080;'>zip<span style='color:#4169E1;'>ngo</span>.zaxx.app</h1>", unsafe_allow_html=True)

tab_home, tab_candidat, tab_employeur = st.tabs(["🏠 Accueil", "🚀 Candidat", "💼 Employeur"])

with tab_home:
    st.markdown("<h2 style='text-align: center; color: #4169E1;'>Votre succès professionnel, propulsé par la précision.</h2>", unsafe_allow_html=True)
    st.warning("🛠️ **Mode Test :** Accès total à toutes les fonctionnalités.")

with tab_candidat:
    st.header("Mon Espace Candidat")
    dossiers = st.tabs(["📂 Candidatures", "📅 Entretiens", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🚀 Campagne"])
    
    with dossiers[2]: # Mes CVs
        st.subheader("📄 Mes CVs enregistrés")
        cvs_enregistres = supabase.table("cvs").select("*").order("created_at", desc=True).execute().data
        if cvs_enregistres:
            for item in cvs_enregistres:
                with st.expander(f"CV pour {item['poste_vise']} - {item['created_at'][:10]}"):
                    st.write(item['contenu'])
        else:
            st.write("Aucun CV enregistré pour le moment.")

    with dossiers[3]: # Relooking CV (Production)
        st.subheader("✨ Relooking & Analyse ATS")
        up = st.file_uploader("1. Upload mon CV", type=["pdf"])
        
        if up:
            if st.button("🚀 Lancer l'analyse ATS"):
                with st.spinner("Analyse en cours..."):
                    reader = PdfReader(up)
                    texte = "".join([p.extract_text() for p in reader.pages])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Agis comme un expert ATS. Analyse ce CV : {texte}. Donne un score sur 100 et liste 3 points critiques."}], 
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.diagnostic = res.choices[0].message.content
            
            if 'diagnostic' in st.session_state:
                st.info(st.session_state.diagnostic)

        st.markdown("---")
        st.subheader("🎯 Adapter mon CV")
        poste = st.text_input("Poste visé")
        style = st.selectbox("Style :", ["Classique", "Moderne", "Créatif"])
        
        if st.button("Valider et Produire"):
            if up and poste:
                with st.spinner("Production et sauvegarde..."):
                    reader = PdfReader(up)
                    texte = "".join([p.extract_text() for p in reader.pages])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Réécris professionnellement ce CV pour le poste de {poste}. Utilise un style {style} : {texte}"}], 
                        model="llama-3.3-70b-versatile"
                    )
                    contenu_final = res.choices[0].message.content
                    
                    # Sauvegarde Supabase
                    supabase.table("cvs").insert({
                        "user_email": "test@test.com",
                        "nom_fichier": f"CV_{poste}.pdf",
                        "contenu": contenu_final,
                        "poste_vise": poste
                    }).execute()
                    
                    st.session_state.cv_final = contenu_final
                    st.success("CV produit et sauvegardé dans 'Mes CVs' !")
            else:
                st.error("Veuillez uploader un CV et renseigner le poste.")

        if 'cv_final' in st.session_state:
            creer_pdf_cv_pro(st.session_state.cv_final, "cv_prod.pdf", style)
            with open("cv_prod.pdf", "rb") as f:
                st.download_button("📥 Télécharger le CV final", f, "mon_cv_final.pdf")

with tab_employeur:
    st.header("Interface Employeur")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div id='cgv-section'></div>", unsafe_allow_html=True)
with st.expander("📜 Lire les Conditions Générales de Vente"):
    afficher_cgv()
st.markdown("<div style='text-align: center;'>© 2026 zipngo.zaxx.app | <a href='#cgv-section'>Voir les CGV</a></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'>Créatrice : Liliane RAKOTOBE | <a href='mailto:creationsites06@gmail.com'>📧</a></div>", unsafe_allow_html=True)
