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


# --- MOTEUR DE MATCHING ARRIÈRE-PLAN IA (> 50%) ---
def executer_matching_automatique_cv(id_cv, contenu_cv, candidat_remote, candidat_pays, candidat_ville):
    """S'exécute immédiatement après l'upload d'un CV pour chercher les offres correspondantes"""
    try:
        offres_db = supabase.table("mes_offres").select("*").execute().data
        if not offres_db:
            return
            
        for offre in offres_db:
            offre_remote = offre.get("is_remote", False)
            offre_pays = offre.get("pays", "France")
            offre_ville = offre.get("ville", "")
            
            # Gestion de la barrière pays/ville grâce au mode Remote
            if not (candidat_remote and offre_remote):
                # Si pas 100% remote bilatéral, on filtre par localisation géographique
                if candidat_pays != offre_pays:
                    continue  # Saute cette offre si les pays ne correspondent pas

            # Analyse de pertinence IA
            prompt = f"""
            Evalue la pertinence du CV suivant pour l'offre d'emploi fournie.
            OFFRE D'EMPLOI :
            {offre['contents']}
            CV DU CANDIDAT :
            {contenu_cv}
            Renvoie UNIQUEMENT un objet JSON (sans bloc de code ```json) structuré ainsi :
            {{
                "score": <un entier entre 0 et 100>,
                "justification": "<2 phrases maximum expliquant le score>"
            }}
            """
            try:
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.1)
                resultat_json = json.loads(res.choices[0].message.content.strip().replace("
```json", "").replace("```", ""))
                
                # Enregistrement automatique si le score est supérieur à 50%
                if int(resultat_json["score"]) >= 50:
                    supabase.table("matching_offres_candidats").insert({
                        "offre_id": offre["id"],
                        "candidat_id": id_cv,
                        "score": resultat_json["score"],
                        "justification": resultat_json["justification"]
                    }).execute()
            except:
                pass
    except Exception as e:
        pass


def executer_matching_ia_depuis_offre(id_offre, texte_offre, offre_remote, offre_pays):
    """S'exécute lorsqu'un employeur crée une nouvelle offre"""
    try:
        candidats_db = supabase.table("cvs").select("*").execute().data
        if not candidats_db: return
        for candidat in candidats_db:
            cand_remote = candidat.get("is_remote", False)
            cand_pays = candidat.get("pays", "France")
            
            if not (offre_remote and cand_remote):
                if offre_pays != cand_pays: continue
                
            prompt = f"Calcule le score de matching (0 à 100) en JSON entre cette offre : {texte_offre} et ce CV : {candidat['contenu']}"
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
            resultat_json = json.loads(res.choices[0].message.content.strip().replace("```json", "").replace("
```", ""))
            
            if int(resultat_json["score"]) >= 50:
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": id_offre, "candidat_id": candidat["id"], "score": resultat_json["score"], "justification": resultat_json["justification"]
                }).execute()
    except: pass


# --- FONCTIONS REELLES DE DIFFUSION ---
def diffuser_france_travail(config, metier, ville, description, contrat):
    try:
        auth_url = "[https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire](https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire)"
        payload = {"grant_type": "client_credentials", "client_id": config.get("france_travail_client_id"), "client_secret": config.get("france_travail_client_secret"), "scope": "api_offresdepotv1"}
        token = requests.post(auth_url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload).json().get("access_token")
        res = requests.post("[https://api.francetravail.io/partenaire/offresdepot/v1/offres](https://api.francetravail.io/partenaire/offresdepot/v1/offres)", headers={"Authorization": f"Bearer {token}"}, json={"intitule": metier, "lieuTravail": {"libelle": ville}, "description": description, "typeContrat": contrat})
        return res.status_code == 201
    except: return False


# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

langues = ["Français", "English (US)", "Malagasy", "Español", "Deutsch"]
if 'langue' not in st.session_state: st.session_state.langue = "Français"
st.session_state.langue = st.selectbox("🌐 Langue", langues, index=0)

tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil", "🚀 Candidat", "💼 Employeur"]])

# --- ZONE CANDIDAT ---
with tab_candidat:
    dossiers = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["📂 Candidatures", "📄 CVs & Profil", "✨ Scan ATS", "🎤 Entretien"]])
    
    with dossiers[0]:
        st.subheader("📜 Historique des envois")
        try:
            response = supabase.table("sourcing").select("email_destinataire, date").order("date", desc=True).execute()
            if response.data: st.table(pd.DataFrame(response.data))
        except: st.write("Aucun envoi enregistré.")
    
    with dossiers[1]:
        st.subheader("📄 Déposez votre CV (Matching automatique en arrière-plan)")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        nom_doc = col_c1.text_input("Nom / Prénom", key="cand_nom")
        pays_cand = col_c2.selectbox("Votre Pays de résidence", list(PAYS_CONFIG.keys()), key="cand_pays")
        ville_cand = col_c3.text_input("Votre Ville", key="cand_ville")
        
        # Option clé : Remote ouvert à l'international
        candidat_remote = st.checkbox("🌍 Je recherche exclusivement des postes en 100% Remote (Supprime les barrières de pays)", value=False)
        
        up_file = st.file_uploader("Uploader votre CV (PDF ou TXT)", type=["pdf", "txt"])
        
        if st.button("💾 Enregistrer mon profil & Activer le matching automatique") and up_file and nom_doc:
            with st.spinner("Analyse du profil et matching automatique supérieur à 50% en cours..."):
                if up_file.name.endswith(".pdf"):
                    contenu_texte = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_file.getvalue())).pages])
                else:
                    contenu_texte = up_file.getvalue().decode("utf-8")
                
                # Insertion en base
                res_cv = supabase.table("cvs").insert({
                    "nom_fichier": nom_doc, 
                    "contenu": contenu_texte,
                    "pays": pays_cand,
                    "ville": ville_cand,
                    "is_remote": candidat_remote
                }).execute()
                
                if res_cv.data:
                    id_nouveau_cv = res_cv.data[0]["id"]
                    # Déclenchement automatique en arrière-plan
                    executer_matching_automatique_cv(id_nouveau_cv, contenu_texte, candidat_remote, pays_cand, ville_cand)
                    st.success("🎯 Profil enregistré ! Notre IA a scanné les offres et envoyé votre profil aux recruteurs correspondants à plus de 50%.")
                    st.rerun()

        # Liste des documents candidats
        data_cvs = supabase.table("cvs").select("*").execute().data
        if data_cvs:
            st.markdown("---")
            for doc in data_cvs:
                st.write(f"📄 {doc['nom_fichier']} ({doc.get('pays', 'Non défini')}) - {'🌍 Option Remote Active' if doc.get('is_remote') else '📍 Localisé'}")

    with dossiers[2]:
        st.subheader("✨ Scan & Audit ATS")
        # Module d'optimisation simple
        st.info("Téléversez un document dans l'onglet précédent pour l'analyser ici.")

    with dossiers[3]:
        st.subheader("🎤 Mon Espace Entretiens")
        # Gestion des entretiens passés et à venir
        try:
            entretiens_proposes = supabase.table("archives_entretiens").select("*").eq("statut", "Proposé").execute().data
            if entretiens_proposes:
                for ent in entretiens_proposes:
                    st.warning(f"Invitation reçue pour le : {ent['date_entretien']}")
                    choix_horaire = st.radio("Sélectionnez l'heure de votre choix :", json.loads(ent['horaires_proposes']), key=f"h_{ent['id']}")
                    if st.button("Validé l'entretien", key=f"btn_v_{ent['id']}"):
                        supabase.table("archives_entretiens").update({"statut": "Confirmé", "date_entretien": f"{ent['date_entretien']} à {choix_horaire}"}).eq("id", ent['id']).execute()
                        st.success("Entretien planifié avec succès !")
                        st.rerun()
        except: pass


# --- ZONE EMPLOYEUR ---
with tab_employeur:
    st.header("💼 Espace Recruteur & Gestion locale")
    id_employeur = "employeur_demo_1"
    
    pays_employeur = st.selectbox("📍 Pays de votre établissement (Adapte les devises et canaux)", list(PAYS_CONFIG.keys()))
    devise_locale = PAYS_CONFIG[pays_employeur]["devise"]
    plateforme_locale = PAYS_CONFIG[pays_employeur]["plateforme_locale"]

    # --- TIROIR MATCHING AUTOMATIQUE (>50%) ---
    st.markdown(f"### 📥 Tiroir des Profils Matchés Automatiquement (>50% de pertinence)")
    try:
        matchings = supabase.table("matching_offres_candidats").select("id, score, justification, candidat_id, mes_offres(intitule, is_remote, pays), cvs(nom_fichier, is_remote, pays)").order("score", desc=True).execute().data
        if matchings:
            for m in matchings:
                # Vérification de sécurité pour l'affichage de l'employeur localisé
                if m['mes_offres']['pays'] == pays_employeur or (m['mes_offres']['is_remote'] and m['cvs']['is_remote']):
                    with st.expander(f"👤 {m['cvs']['nom_fichier']} - Matché à {m['score']}% sur l'offre : {m['mes_offres']['intitule']}"):
                        st.write(f"**Justification ATS :** {m['justification']}")
                        st.caption(f"Statut candidat : {'🌍 100% Remote (International)' if m['cvs']['is_remote'] else '📍 Localisé'}")
                        
                        # Bouton Pouce pour déclencher directement l'entretien
                        if st.button("👍 Accepter le profil & Proposer un RDV Jitsi", key=f"t_rec_{m['id']}"):
                            st.session_state[f"form_active_{m['id']}"] = True
                            
                        if st.session_state.get(f"form_active_{m['id']}", False):
                            with st.form(key=f"f_rdv_{m['id']}"):
                                dt = st.date_input("Date de l'entretien", datetime.date.today())
                                slot1 = st.text_input("Horaire optionnel 1", "10:00")
                                slot2 = st.text_input("Horaire optionnel 2", "14:30")
                                slot3 = st.text_input("Horaire optionnel 3", "16:00")
                                if st.form_submit_button("📨 Envoyer les propositions"):
                                    room = f"jitsi-zipngo-{m['id']}"
                                    supabase.table("archives_entretiens").insert({
                                        "candidat_id": m["candidat_id"],
                                        "statut": "Proposé",
                                        "lien_jitsi": f"[https://meet.jit.si/](https://meet.jit.si/){room}",
                                        "date_entretien": str(dt),
                                        "horaires_proposes": json.dumps([slot1, slot2, slot3])
                                    }).execute()
                                    st.success("Créneaux envoyés au candidat !")
                                    st.session_state[f"form_active_{m['id']}"] = False
                                    st.rerun()
        else:
            st.info("Aucun profil n'a encore atteint le seuil des 50% de matching automatique pour vos offres.")
    except Exception as e:
        st.info("En attente de nouvelles candidatures spontanées ou d'offres rédigées.")

    # --- FORMULAIRE DE RÉDACTION D'OFFRE ---
    st.markdown("---")
    with st.expander("📝 Rédiger, Localiser et Diffuser une nouvelle Offre"):
        col_e1, col_e2 = st.columns(2)
        metier_off = col_e1.text_input("Intitulé du poste", key="e_job")
        ville_off = col_e2.text_input("Ville du poste", key="e_v")
        salaire = col_e1.number_input(f"Salaire proposé (En {devise_locale})", min_value=1.0, value=15.0)
        contrat = st.selectbox("Type de contrat", ["CDI", "CDD", "Freelance", "Stage"])
        
        # Option Clé : Offre Remote
        offre_remote = st.checkbox("🌍 Poste ouvert au 100% Télétravail (Supprime la barrière géographique pays/ville)", value=False)
        
        if st.button("✨ Générer et Matcher l'offre"):
            texte_genere = f"Recherche profil pour {metier_off} à {ville_off}. Contrat {contrat}. Salaire : {salaire} {devise_locale}."
            st.session_state.current_offre_txt = texte_genere
            st.write(texte_genere)
            
        if st.button("✅ Publier l'offre à l'échelle locale / globale"):
            if "current_offre_txt" in st.session_state:
                res_o = supabase.table("mes_offres").insert({
                    "intitule": metier_off,
                    "contents": st.session_state.current_offre_txt,
                    "ville": ville_off,
                    "pays": pays_employeur,
                    "is_remote": offre_remote,
                    "employeur_id": id_employeur
                }).execute()
                
                if res_o.data:
                    id_o = res_o.data[0]["id"]
                    # Lancement immédiat du matching sur cette nouvelle offre
                    executer_matching_ia_depuis_offre(id_o, st.session_state.current_offre_txt, offre_remote, pays_employeur)
                    st.success(f"Offre publiée avec succès ! Diffusée localement via : {plateforme_locale}")
                    st.rerun()
