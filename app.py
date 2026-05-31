import streamlit as st
import datetime
import pandas as pd
import io
import re
import json
import urllib.parse
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
from fpdf import FPDF
import resend

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- FONCTIONS D'ORIGINE ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

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
    texte_cgv = "1. Accès Candidat 6€/3mois | Recruteur 39€/mois. 2. Limites Gratuit : 1 CV/mois, 1 campagne/mois. 3. Premium : 3 CVs/semaine, 20 mails/jour."
    st.markdown(traduire_avec_ia(texte_cgv, st.session_state.langue))

def obtenir_contenu_structure(txt_cv, metier):
    prompt = f"Analyse pour le poste '{metier}'. Retourne uniquement un JSON structuré avec: 'header' (nom, titre_poste, contact), 'sidebar' (contenu), 'main' (titre, corps), 'mots_cles_ajoutes'. CV: {txt_cv}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return json.loads(res.choices[0].message.content.replace("```json", "").replace("```", ""))

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

# --- MOTEUR DE TRI AUTOMATIQUE (Corrigé syntaxique) ---
def trier_candidats_auto(offre_data):
    profils = supabase.table("candidats").select("*").execute().data
    for p in profils:
        prompt = "Compare le CV: {} et l'Offre: {}. Score 0-100. Retourne un JSON strictement comme ceci: {{\"score\": 0}}".format(
            p.get('cv_text', 'Non disponible'), offre_data
        )
        res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        try:
            score = json.loads(res.choices[0].message.content.replace("```json", "").replace("```", "")).get('score', 0)
            statut = "Matchs" if score >= 50 else "Vivier"
            supabase.table("candidats").update({"statut": statut, "score": score}).eq("id", p['id']).execute()
        except: continue

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

langues = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"]
st.session_state.langue = st.sidebar.selectbox("🌐 Sélectionner votre langue", langues, index=0)

# Présentation officielle
st.markdown(f"""
<div style='background-color: #eef2f7; padding: 25px; border-radius: 15px; border-left: 6px solid #4169E1;'>
    <h3 style='color: #000080; margin-top: 0;'>{traduire_avec_ia("Bienvenue sur zipngo", st.session_state.langue)}</h3>
    <p style='font-size: 16px;'>{traduire_avec_ia("L'application intelligente au service de votre trajectoire professionnelle. Optimisez vos démarches, facilitez vos interactions et accélérez votre réussite grâce à notre écosystème conçu pour accompagner chaque étape de votre carrière.", st.session_state.langue)}</p>
</div>
""", unsafe_allow_html=True)

with st.expander(traduire_avec_ia("📜 Lire les CGV", st.session_state.langue)): afficher_cgv()
st.checkbox(traduire_avec_ia("J'accepte les CGV", st.session_state.langue), key="accept_cgv")

tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil", "🚀 Candidat", "💼 Employeur"]])

with tab_candidat:
    dossiers = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["📂 Candidatures", "📄 CVs", "✨ Relooking CV", "🌐 Sourcing", "🎤 Entretien"]])
    
    with dossiers[0]:
        st.subheader("📜 Historique des envois")
        try:
            response = supabase.table("sourcing").select("email_destinataire, date").order("date", desc=True).execute()
            if response.data: st.table(pd.DataFrame(response.data))
        except Exception as e: st.error(f"Erreur : {e}")

    with dossiers[1]:
        st.subheader("📄 Mes Documents & CVs")
        type_doc = st.selectbox("Type", ["CV", "Lettre de Motivation"])
        nom_doc = st.text_input("Nom du document")
        up_file = st.file_uploader("Uploader le fichier", type=["pdf", "txt"])
        if st.button("💾 Enregistrer") and up_file and nom_doc:
            supabase.table("cvs").insert({"nom_fichier": f"{nom_doc}_{type_doc}", "contenu": str(up_file.getvalue()), "type_document": type_doc}).execute()
            st.rerun()
        data = supabase.table("cvs").select("nom_fichier, contenu").execute().data
        if data:
            for doc in data:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📄 {doc['nom_fichier']}")
                c2.download_button("⬇️ Télécharger", data=doc['contenu'], file_name=f"{doc['nom_fichier']}.pdf")

    with dossiers[2]:
        st.subheader("✨ Relooking & Scoring ATS")
        metier = st.text_area("Intitulé du poste ou offre...")
        up = st.file_uploader("Upload CV", type=["pdf"])
        if up and metier and st.button("🚀 Optimiser & Designer"):
            txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
            data = obtenir_contenu_structure(txt, metier)
            pdf = FPDF(); pdf.add_page(); appliquer_design_geometrique(pdf, data)
            st.session_state.pdf_final = pdf.output(dest='S').encode('latin-1')
            st.success("✅ Mots-clés intégrés : " + ", ".join(data['mots_cles_ajoutes']))
            st.download_button("⬇️ Télécharger CV Design", data=st.session_state.pdf_final, file_name=f"CV_{metier[:10]}.pdf")

    with dossiers[3]: # SOURCING
        st.subheader("🌐 Prospection Spontanée")
        domaines = ["Restauration & Fast-Food", "Informatique & Tech", "Hôtellerie & Tourisme", "Santé & Services à la personne", "Commerce & Distribution", "BTP & Immobilier", "Logistique & Transport", "Finance & Juridique", "Marketing, Com & Art", "Industrie & Agriculture", "Administration publique"]
        col1, col2, col3 = st.columns([1, 1, 1])
        cat = col1.selectbox("Domaine élargi", sorted(domaines))
        ville = col2.text_input("Ville cible")
        dist = col3.slider("Rayon (km)", 0, 100, 20)
        
        if st.button("🔍 Rechercher 20 nouveaux contacts") and ville:
            deja = [i['email_destinataire'] for i in supabase.table("sourcing").select("email_destinataire").execute().data]
            prompt = f"Donne 20 adresses emails professionnelles uniquement pour le domaine '{cat}' à '{ville}' dans un rayon de {dist}km. Exclus ceux-ci : {','.join(deja)}. Format : retourne uniquement une liste d'emails séparés par des virgules, aucun texte supplémentaire."
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.session_state.emails = [e.strip() for e in res.replace('\n', '').split(',')]
            st.rerun()
            
        if 'emails' in st.session_state and len(st.session_state.emails) >= 20:
            st.write(f"Cibles : {', '.join(st.session_state.emails)}")
            msg = st.text_area("Message :", f"Madame, Monsieur, je porte un vif intérêt à votre établissement à {ville} dans le secteur de {cat}. Fort(e) d'une expérience pertinente, je vous propose ma candidature. Vous trouverez mon CV en pièce jointe.", height=200)
            up_cv = st.file_uploader("CV en PJ", type=["pdf"])
            if st.button("🚀 Envoyer à 20 contacts") and up_cv:
                resend.Emails.send({"from": "contact@zipngo.zaxx.app", "to": st.session_state.emails[0], "bcc": st.session_state.emails[1:20], "subject": f"Candidature - {cat}", "text": msg, "attachments": [{"filename": "Mon_CV.pdf", "content": list(up_cv.getvalue())}]})
                for e in st.session_state.emails[:20]: supabase.table("sourcing").insert({"email_destinataire": e, "date": str(datetime.date.today())}).execute()
                st.success("✅ Campagne envoyée (1 destinataire + 19 BCC) !")
                st.rerun()

    with dossiers[4]:
        st.subheader("🎤 Simulateur d'entretien")
        if st.button("Démarrer la simulation"):
            st.session_state.quest = client.chat.completions.create(messages=[{"role": "user", "content": "Pose 3 questions d'entretien pour ce profil."}], model="llama-3.3-70b-versatile").choices[0].message.content
        if 'quest' in st.session_state:
            st.write(st.session_state.quest)
            rep = st.text_area("Votre réponse :")
            if st.button("Évaluer"):
                score = client.chat.completions.create(messages=[{"role": "user", "content": f"Note cette réponse sur 20 : {rep}"}], model="llama-3.3-70b-versatile").choices[0].message.content
                st.info(score)

with tab_employeur:
    tiroirs = st.tabs(["🔥 Matchs", "📂 Vivier", "👤 Profils", "📅 Entretiens", "🗄️ Archives"])
    with tiroirs[0]: # Matchs
        st.subheader("🔥 Matchs (Score > 50%)")
        matchs = supabase.table("candidats").select("*").gte("score", 50).execute().data
        for c in matchs:
            with st.expander(f"{c.get('nom_candidat')} - Score: {c.get('score')}%"):
                if st.button(f"👍 Offrir Entretien", key=f"match_{c['id']}"): st.success("Entretien proposé !")
    with tiroirs[1]: # Vivier
        st.subheader("📂 Vivier")
        trier_candidats_auto({"post": "Publication en cours"}) # Exemple de lancement
        st.write("Vivier des candidats (Score < 50%)")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """<div style='text-align: center;'>
        <p>zipngo 2026 - Système complet | Créé par <b>Liliane RAKOTOBE</b></p>
        <p>Contact : <a href='mailto:creationsites06@gmail.com'>📧 creationsites06@gmail.com</a></p>
    </div>""", unsafe_allow_html=True
)
