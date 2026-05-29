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

# Initialisation de l'email pour le RLS
if 'user_email' not in st.session_state: st.session_state.user_email = "test@exemple.com"

# --- FONCTION TRADUCTION IA ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

# --- FONCTIONS D'ORIGINE ---
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

def archiver_entretien(candidat_id, statut, lien_jitsi, feedback=""):
    # Ajout du champ email pour la sécurité
    supabase.table("archives_entretiens").insert({
        "candidat_id": candidat_id,
        "statut": statut,
        "lien_jitsi": lien_jitsi,
        "feedback": feedback,
        "date_archivage": str(datetime.datetime.now()),
        "email": st.session_state.user_email
    }).execute()

# --- NOUVELLES FONCTIONS ---
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
            response = supabase.table("sourcing").select("email_destinataire, date").eq("email", st.session_state.user_email).order("date", desc=True).execute()
            if response.data: st.table(pd.DataFrame(response.data))
        except Exception as e: st.error(f"Erreur : {e}")
    with dossiers[1]:
        st.subheader("📄 Mes Documents & CVs")
        type_doc = st.selectbox("Type", ["CV", "Lettre de Motivation"])
        nom_doc = st.text_input("Nom du document")
        up_file = st.file_uploader("Uploader le fichier", type=["pdf", "txt"])
        if st.button("💾 Enregistrer") and up_file and nom_doc:
            supabase.table("cvs").insert({"nom_fichier": f"{nom_doc}_{type_doc}", "contenu": str(up_file.getvalue()), "type_document": type_doc, "email": st.session_state.user_email}).execute()
            st.rerun()
        data = supabase.table("cvs").select("nom_fichier, contenu").eq("email", st.session_state.user_email).execute().data
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
    with dossiers[3]:
        st.subheader("🌐 Prospection Spontanée")
        domaines = ["Restauration", "Informatique", "Hôtellerie", "Santé", "Commerce", "BTP", "Logistique", "Finance", "Marketing"]
        col1, col2 = st.columns(2)
        cat = col1.selectbox("Domaine", domaines)
        ville = col2.text_input("Ville cible")
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            prompt = f"Donne 20 emails pros pour '{cat}' à '{ville}'. Liste séparée par virgules."
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.session_state.emails = [e.strip() for e in res.split(',')]
            st.rerun()
        if 'emails' in st.session_state:
            msg = st.text_area("Message :", f"Madame, Monsieur, je porte un vif intérêt à votre établissement à {ville} dans le secteur de {cat}. Fort(e) d'une expérience pertinente, je vous propose ma candidature. Vous trouverez mon CV en pièce jointe.", height=200)
            dest, bcc = st.session_state.emails[0], ",".join(st.session_state.emails[1:])
            mailto = f"mailto:{dest}?bcc={bcc}&subject={urllib.parse.quote('Candidature - zipngo')}&body={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{mailto}" style="padding:10px; background:#4169E1; color:white; border-radius:5px; text-decoration:none;">📤 Envoyer via mon email (Levée d\'anonymat)</a>', unsafe_allow_html=True)
            if st.button("💾 Enregistrer"): 
                supabase.table("sourcing").insert({"email_destinataire": str(st.session_state.emails), "email": st.session_state.user_email}).execute()
                st.success("Campagne enregistrée !")
    with dossiers[4]:
        st.subheader("🎤 Simulateur d'entretien")
        if st.button("Démarrer la simulation"):
            st.session_state.quest = client.chat.completions.create(messages=[{"role": "user", "content": "Pose 3 questions d'entretien."}], model="llama-3.3-70b-versatile").choices[0].message.content
        if 'quest' in st.session_state:
            st.write(st.session_state.quest)
            rep = st.text_area("Votre réponse :")
            if st.button("Évaluer et lever l'anonymat"):
                lien = f"https://meet.jit.si/zipngo_{st.session_state.user_email.split('@')[0]}"
                archiver_entretien("Candidat", "Terminé", lien, "Score 16/20")
                st.info(f"Lien entretien : {lien}")
                st.success("Données révélées à l'employeur ! 👍")

with tab_employeur:
    st.header("💼 Interface Recrutement")
    with st.expander("📝 Rédiger et Diffuser une Offre", expanded=True):
        col1, col2 = st.columns(2)
        metier = col1.text_input("Métier")
        ville = col2.text_input("Ville")
        salaire = col1.number_input("Taux horaire (€)", min_value=10.0, step=0.5)
        nb_heures = col2.number_input("Nombre d'heures", min_value=0, step=1)
        rythme = st.selectbox("Rythme", ["Fixe", "2x8", "3x8", "Nuit", "Week-end", "Variable"])
        contrat = st.selectbox("Contrat", ["CDI", "CDD", "Intérim", "Alternance", "Stage"])
        is_remote = st.checkbox("100% Remote")
        if st.button("✨ Générer l'offre"):
            prompt = f"Rédige une offre pour {metier} à {ville}, {contrat}, {salaire}€/h, {nb_heures}h/semaine, rythme {rythme}. Remote: {is_remote}."
            st.session_state.offre_texte = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.write(st.session_state.offre_texte)
        emails_agences = st.text_input("Emails Agences (séparés par virgule)")
        if emails_agences:
            dest = emails_agences.split(',')[0]
            mailto = f"mailto:{dest}?subject={urllib.parse.quote('Offre d\'emploi')}&body={urllib.parse.quote(st.session_state.get('offre_texte', ''))}"
            st.markdown(f'<a href="{mailto}" style="padding:10px; background:#28a745; color:white; border-radius:5px; text-decoration:none;">📤 Diffuser via mon email (Levée d\'anonymat)</a>', unsafe_allow_html=True)
        if st.button("✅ Valider"):
            if 'offre_texte' in st.session_state:
                supabase.table("mes_offres").insert({"intitule": metier, "contenu": st.session_state.offre_texte, "ville": ville, "email": st.session_state.user_email}).execute()
                st.success("Offre enregistrée !")
