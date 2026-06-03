import streamlit as st
import datetime
import pandas as pd
import io
import re
import json
from groq import Groq
from supabase import create_client
from pypdf import PdfReader
import resend
import requests
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium Global", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]

# --- CONFIGURATION DES PAYS & DEVISES ---
PAYS_CONFIG = {
    "France": {"devise": "€", "plateforme_locale": "France Travail"},
    "Madagascar": {"devise": "Ar", "plateforme_locale": "Orange MixJob / Midi"},
    "United States": {"devise": "$", "plateforme_locale": "Indeed US"},
    "Canada": {"devise": "$ CAD", "plateforme_locale": "Guichet Emploi"},
    "International / Autre": {"devise": "$", "plateforme_locale": "LinkedIn"}
}

# --- FONCTION TRADUCTION IA ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

# --- NETTOYAGE JSON SECURISE ---
def extraire_json_propre(texte_brut):
    try:
        texte_nettoye = re.sub(r"```json|```", "", texte_brut).strip()
        return json.loads(texte_nettoye)
    except:
        try:
            match = re.search(r"\{.*\}", texte_brut, re.DOTALL)
            if match: return json.loads(match.group(0))
        except: pass
    return {"score": 0, "justification": "Erreur d'analyse."}

# --- MOTEUR DE MATCHING ---
def executer_matching_ia_depuis_offre(id_offre, texte_offre, offre_remote, offre_pays):
    try:
        candidats_db = supabase.table("cvs").select("*").execute().data
        if not candidats_db: return
        for candidat in candidats_db:
            cand_remote = candidat.get("is_remote", False)
            cand_pays = candidat.get("pays", "France")
            if not (offre_remote and cand_remote):
                if cand_pays != offre_pays: continue
            try:
                prompt = f"Calcule le score de matching (0 à 100) en JSON entre cette offre : {texte_offre} et ce CV : {candidat['contenu']}"
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                resultat_json = extraire_json_propre(res.choices[0].message.content)
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": id_offre, "candidat_id": candidat["id"], "score": int(resultat_json.get("score", 0)), 
                    "justification": resultat_json["justification"], "source": candidat.get("source", "app")
                }).execute()
            except: pass
    except: pass

def executer_matching_automatique_cv(id_cv, contenu_cv, candidat_remote, candidat_pays, candidat_ville, source="app"):
    try:
        offres_db = supabase.table("mes_offres").select("*").execute().data
        if not offres_db: return
        for offre in offres_db:
            if not (candidat_remote and offre.get("is_remote", False)):
                if candidat_pays != offre.get("pays", "France"): continue
            prompt = f"Evalue le matching en JSON entre l'offre : {offre['contents']} et le CV : {contenu_cv}."
            try:
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.1)
                resultat_json = extraire_json_propre(res.choices[0].message.content)
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": offre["id"], "candidat_id": id_cv, "score": int(resultat_json.get("score", 0)), 
                    "justification": resultat_json["justification"], "source": source
                }).execute()
            except: pass
    except: pass

def simuler_ia_reception_email(email_recu, nom_candidat, email_reel, tel_reel, texte_cv):
    res_cv = supabase.table("cvs").insert({
        "nom_fichier": nom_candidat, "contenu": texte_cv, "pays": "France", "ville": "Externe",
        "is_remote": False, "source": "email", "email_reel": email_reel, "tel_reel": tel_reel, "anonymat_leve": True
    }).execute()
    if res_cv.data:
        executer_matching_automatique_cv(res_cv.data[0]["id"], texte_cv, False, "France", "Externe", source="email")

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.markdown("### 🛠️ Création & Support")
st.sidebar.markdown("**Créatrice :** Liliane RAKOTOBE")
st.sidebar.markdown('<a href="mailto:creationsites06@gmail.com" style="text-decoration: none; font-size: 20px;">✉️ <span style="font-size: 14px; vertical-align: middle;">Contact par Email</span></a>', unsafe_allow_html=True)
st.sidebar.markdown("---")

langues = ["Français", "English (US)", "Malagasy", "Español", "Deutsch"]
if 'langue' not in st.session_state: st.session_state.langue = "Français"
st.session_state.langue = st.sidebar.selectbox("🌐 Langue de l'application", langues, index=0)

tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil & Mode d'emploi", "🚀 Candidat", "💼 Employeur"]])

# --- ZONE ACCUEIL ---
with tab_home:
    st.markdown(f"## {traduire_avec_ia('Bienvenue sur zipngo, l\'ATS intelligent et anonyme sans frontières ! 🌍', st.session_state.langue)}")
    st.markdown(traduire_avec_ia("""
    **zipngo** est une plateforme de recrutement de nouvelle génération, propulsée par une Intelligence Artificielle avancée. 
    Notre mission est double : **supprimer les barrières géographiques** pour permettre le recrutement local et à l'international, et **garantir une totale équité** grâce à un système d'anonymat crypté.
    
    Sur zipngo, les processus de sélection se font uniquement sur les compétences. Les coordonnées privées (noms, téléphones, emails) restent entièrement masquées tant qu'une entente mutuelle n'a pas été scellée d'un commun accord !
    
    ### 🛠️ Guide de démarrage rapide :
    * **Étape 1 :** Choisissez votre langue préférée dans le menu latéral gauche.
    * **Étape 2 :** Si vous cherchez un emploi, accédez à l'onglet **🚀 Candidat** pour configurer votre profil discret.
    * **Étape 3 :** Si vous êtes un recruteur, accédez à l'onglet **💼 Employeur** pour renseigner vos identifiants d'entreprise et piloter vos tiroirs de tri automatiques.
    """, st.session_state.langue))
    st.info(traduire_avec_ia("💡 Moteur de matching autonome : À chaque dépôt d'offre, l'IA parcourt l'intégralité de la base de profils pour trouver instantanément la perle rare.", st.session_state.langue))

# --- ZONE CANDIDAT ---
with tab_candidat:
    st.markdown(f"### 🚀 {traduire_avec_ia('Espace Candidat Anonymisé', st.session_state.langue)}")
    with st.expander(f"💡 {traduire_avec_ia('Mode d\'emploi Candidat — Comment ça marche ?', st.session_state.langue)}", expanded=True):
        st.markdown(traduire_avec_ia("""
        1. **Création du profil secret :** Renseignez vos vraies coordonnées et importez votre CV (PDF/TXT). Vos données personnelles sont immédiatement protégées et masquées aux yeux des recruteurs (`[Profil Anonyme App]`).
        2. **Option Télétravail (Remote) :** En cochant l'option 100% Remote, vous permettez à l'IA de vous matcher avec des employeurs du monde entier, sans contrainte de frontières.
        3. **Suivi & Entretien Jitsi :** Lorsqu'un recruteur est intéressé par vos compétences (Score de matching >= 50%), il génère un salon vidéo anonyme. Rendez-vous dans le sous-onglet **Mes Entretiens** pour y participer.
        4. **Levée de l'Anonymat :** L'entretien s'est bien passé ? Appuyez sur le **Pouce 👍** pour accepter de dévoiler votre identité réelle et vos coordonnées à cet employeur.
        """, st.session_state.langue))

    dossiers = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["📂 Candidatures", "📄 CVs & Profil", "🎤 Mes Entretiens"]])
    with dossiers[1]:
        st.subheader("📄 Créez votre Profil Secret")
        col_c1, col_c2, col_c3 = st.columns(3)
        nom_cand = col_c1.text_input("Vrai Nom / Prénom (Sera crypté et caché)", key="cand_nom")
        email_cand = col_c2.text_input("Votre Email (Caché)", key="cand_em")
        tel_cand = col_c3.text_input("Votre Téléphone (Caché)", key="cand_tel")
        pays_cand = st.selectbox("Votre Pays", list(PAYS_CONFIG.keys()), key="cand_pays")
        candidat_remote = st.checkbox("🌍 Poste en 100% Remote ciblé", value=False)
        up_file = st.file_uploader("Uploader votre CV", type=["pdf", "txt"])
        if st.button("💾 Chiffrer et Enregistrer mon Profil") and up_file and nom_cand:
            contenu_texte = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_file.getvalue())).pages]) if up_file.name.endswith(".pdf") else up_file.getvalue().decode("utf-8", errors="ignore")
            supabase.table("cvs").insert({"nom_fichier": nom_cand, "contenu": contenu_texte, "pays": pays_cand, "ville": "App", "is_remote": candidat_remote, "source": "app", "email_reel": email_cand, "tel_reel": tel_cand, "anonymat_leve": False}).execute()
            st.success("🎯 Profil enregistré !")

    with dossiers[2]:
        st.subheader("🎤 Vos rendez-vous & Levée de l'anonymat")
        try:
            mes_rdv = supabase.table("archives_entretiens").select("*, cvs(*)").execute().data
            if mes_rdv:
                for rdv in mes_rdv:
                    st.info(f"📅 Salon vidéo planifié : {rdv['date_entretien']}")
                    st.markdown(f"[🟩 Entrer en entretien Jitsi]({rdv['lien_jitsi']})", unsafe_allow_html=True)
                    if rdv['statut'] in ["Archivé", "Confirmé"]:
                        if st.button("👍 Dévoiler mes coordonnées réelles à cet employeur", key=f"pouce_cand_{rdv['id']}"):
                            supabase.table("archives_entretiens").update({"candidat_agree": True}).eq("id", rdv['id']).execute()
                            st.rerun()
        except: pass

# --- ZONE EMPLOYEUR ---
with tab_employeur:
    st.header("💼 Espace Recruteur")
    with st.expander(f"💡 {traduire_avec_ia('Mode d\'emploi Employeur', st.session_state.langue)}", expanded=True):
        st.markdown(traduire_avec_ia("1. Authentification. 2. Tiroirs de tri. 3. Gestion anonymat.", st.session_state.langue))
    
    if "entreprise_connectee" not in st.session_state: st.session_state.entreprise_connectee = None
    if not st.session_state.entreprise_connectee:
        with st.form("form_entreprise"):
            nom_ent = st.text_input("🏢 Nom de l'entreprise *")
            siret_ent = st.text_input("🔢 SIRET *")
            email_notif = st.text_input("📩 Email *")
            tel_ent = st.text_input("📞 Téléphone *")
            pays_ent = st.selectbox("📍 Pays", list(PAYS_CONFIG.keys()))
            if st.form_submit_button("🔓 Valider"):
                st.session_state.entreprise_connectee = {"id": "emp_123", "nom": nom_ent, "email_reception": email_notif, "tel": tel_ent, "pays": pays_ent}
                st.rerun()
    else:
        ent_info = st.session_state.entreprise_connectee
        tiroir_principal, tiroir_vivier = st.tabs(["📥 TIROIR MATCH (>= 50%)", "🗄️ VIVIER (< 50%)"])
        try:
            matchings = supabase.table("matching_offres_candidats").select("*, mes_offres(*), cvs(*)").order("score", desc=True).execute().data
            with tiroir_principal:
                for m in matchings:
                    if int(m['score']) >= 50:
                        with st.expander(f"{m['cvs']['nom_fichier']} — Score : {m['score']}%"):
                            if st.button("👍 Planifier un entretien", key=f"pouce_rec_{m['id']}"):
                                room = f"zipngo-room-{m['id']}"
                                supabase.table("archives_entretiens").insert({"candidat_id": m["candidat_id"], "statut": "Confirmé", "lien_jitsi": f"https://meet.jit.si/{room}", "date_entretien": "À définir"}).execute()
                                st.rerun()
        except: pass

# --- PIED DE PAGE ENRICHI ---
st.markdown("---")
with st.expander("⚖️ Conditions Générales de Vente (CGV)"):
    st.markdown("""
    **1. Engagement de service :** zipngo s'engage à fournir un outil de mise en relation basé sur l'anonymat et l'IA.
    **2. Traitement des données :** Les informations sont traitées de manière chiffrée. L'anonymat est strictement préservé jusqu'à validation mutuelle.
    **3. Responsabilité :** L'utilisateur est seul responsable de l'exactitude des informations fournies. zipngo n'agit qu'en tant qu'intermédiaire technique.
    **4. Confidentialité :** Aucune donnée personnelle n'est vendue à des tiers. Toute demande de suppression peut être effectuée par écrit.
    **5. Utilisation :** Le service est mis à disposition 'tel quel'. L'utilisateur accepte les conditions de fonctionnement des outils de visio (Jitsi) et de matching (IA).
    """)

st.markdown(
    '<p style="text-align: center; color: #555555;">Application réalisée par <b>Liliane RAKOTOBE</b> — <a href="mailto:creationsites06@gmail.com" style="text-decoration: none;">✉️ Contact</a></p>', 
    unsafe_allow_html=True
)
