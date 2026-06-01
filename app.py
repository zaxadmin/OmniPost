import streamlit as st
import datetime, pandas as pd, io, json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- FONCTIONS ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

def afficher_cgv():
    st.markdown("### Conditions Générales de Vente")
    st.markdown("1. **Accès Candidat** : 6€ / 3 mois. 2. **Accès Recruteur** : 39€ / mois. 3. **Limites Gratuit** : 1 CV/mois, 1 campagne/mois. 4. **Premium** : 3 CVs/semaine, 20 mails/jour.")

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse pour le poste '{metier}'. Retourne uniquement un JSON structuré avec: 'header' (nom, titre_poste, contact), 'sidebar' (contenu), 'main' (titre, corps), 'mots_cles_ajoutes'. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("
```", ""))

def appliquer_design_geometrique(pdf, data):
    pdf.set_fill_color(52, 73, 94); pdf.rect(0, 0, 60, 300, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(5, 10); pdf.set_font("Arial", 'B', 16); pdf.cell(50, 10, data['header']['nom'], ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 5, data['header']['contact'])
    pdf.set_xy(5, 50); pdf.set_font("Arial", 'B', 14); pdf.cell(50, 10, "COMPÉTENCES", ln=True)
    pdf.set_font("Arial", size=10); pdf.multi_cell(50, 7, data['sidebar']['contenu'])
    pdf.set_text_color(0, 0, 0); pdf.set_xy(70, 10); pdf.set_font("Arial", 'B', 18); pdf.cell(100, 10, data['header']['titre_poste'], ln=True)
    pdf.set_xy(70, 30); pdf.set_font("Arial", 'B', 14); pdf.cell(100, 10, data['main']['titre'], ln=True)
    pdf.set_xy(70, 45); pdf.set_font("Arial", size=11); pdf.multi_cell(130, 7, data['main']['corps'])

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

langues = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"]
if 'langue' not in st.session_state: st.session_state.langue = "Français"
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue", langues, index=0)

st.markdown(f"""
<div style='background-color: #eef2f7; padding: 25px; border-radius: 15px; border-left: 6px solid #4169E1;'>
    <h3 style='color: #000080; margin-top: 0;'>{traduire_avec_ia("Bienvenue sur zipngo", st.session_state.langue)}</h3>
    <p style='font-size: 16px;'>{traduire_avec_ia("L'application intelligente au service de votre trajectoire professionnelle. Optimisez vos démarches, facilitez vos interactions et accélérez votre réussite grâce à notre écosystème conçu pour accompagner chaque étape de votre carrière.", st.session_state.langue)}</p>
    <p style='font-size: 14px;'><strong>{traduire_avec_ia("Le Système du Pouce 👍 :", st.session_state.langue)}</strong> {traduire_avec_ia("Cliquez sur le pouce pour débloquer l'agenda, planifier votre visio, et le valider à deux pour lever l'anonymat et échanger vos coordonnées.", st.session_state.langue)}</p>
</div>
""", unsafe_allow_html=True)

# Barre latérale Premium
st.sidebar.markdown("### 💎 Accès Premium")
st.sidebar.link_button("Premium Candidat (6€/3mois)", "https://buy.stripe.com/9B6fZa08JeJZ9UScUQeIw04")
st.sidebar.link_button("Premium Recruteur (39€/mois)", "https://buy.stripe.com/7sY9AM3kVfO3aYW6wseIw03")

# Tabs
tab_home, tab_candidat, tab_employeur, tab_matching = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil", "🚀 Candidat", "💼 Employeur", "🔄 Matching"]])

with tab_home:
    with st.expander(traduire_avec_ia("📜 Lire les CGV", st.session_state.langue)): afficher_cgv()
    st.checkbox(traduire_avec_ia("J'accepte les CGV", st.session_state.langue), key="accept_cgv")

with tab_candidat:
    dossiers = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["📂 Candidatures", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🎤 Entretien"]])
    with dossiers[0]:
        response = supabase.table("sourcing").select("email_destinataire, date").order("date", desc=True).execute()
        if response.data: st.table(pd.DataFrame(response.data))
    with dossiers[1]:
        type_doc = st.selectbox("Type", ["CV", "Lettre de Motivation"])
        nom_doc = st.text_input("Nom du document")
        up_file = st.file_uploader("Uploader", type=["pdf", "txt"])
        if st.button("💾 Enregistrer") and up_file and nom_doc:
            supabase.table("cvs").insert({"nom_fichier": f"{nom_doc}_{type_doc}", "contenu": str(up_file.getvalue()), "type_document": type_doc}).execute()
            st.rerun()
    with dossiers[2]:
        metier = st.text_area("Intitulé du poste...")
        up = st.file_uploader("Upload CV", type=["pdf"])
        if up and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            st.session_state.pdf_final = pdf.output(dest='S').encode('latin-1')
            st.download_button("⬇️ Télécharger CV Design", data=st.session_state.pdf_final, file_name=f"CV_{metier[:10]}.pdf")
    with dossiers[3]:
        doms = ["Restauration", "Informatique", "Hôtellerie", "Santé", "Commerce", "BTP", "Logistique", "Finance", "Marketing"]
        cat = st.selectbox("Domaine", doms)
        ville = st.text_input("Ville cible")
        is_remote = st.checkbox("Recherche uniquement en Remote")
        if st.button("🔍 Rechercher"): st.success("Recherche lancée...")
    with dossiers[4]:
        st.subheader("🎤 Simulateur d'entretien")
        if st.button("👍 Débloquer l'agenda"): st.session_state.agenda = True

with tab_employeur:
    st.header("💼 Interface Recrutement")
    metier = st.text_input("Métier")
    ville = st.text_input("Ville")
    if st.button("✨ Générer l'offre"): st.write("Offre générée...")
    if st.button("✅ Valider et Diffuser"): supabase.table("mes_offres").insert({"intitule": metier, "ville": ville}).execute()

with tab_matching:
    st.subheader("🔄 Matching Bidirectionnel")
    if st.button("👍 Valider fin entretien"): st.success("Anonymat levé, coordonnées accessibles.")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #555555; padding: 20px;'>
        <p>Créatrice : <b>Liliane RAKOTOBE</b></p>
        <p><a href='mailto:creationsites06@gmail.com' style='text-decoration: none; font-size: 24px;'>📧</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
