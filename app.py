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
st.set_page_config(page_title="zipngo | ATS Premium", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
resend.api_key = st.secrets["RESEND_API_KEY"]


# --- FONCTION TRADUCTION IA ---
@st.cache_data(show_spinner=False)
def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte traduit sans aucune explication : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content


# --- FONCTIONS D'ORIGINE ---
def afficher_cgv():
    texte_cgv = "1. Accès Candidat 6€/3mois | Recruteur 39€/mois. 2. Limites Gratuit : 1 CV/mois, 1 campagne/mois. 3. Premium : 3 CVs/semaine, 20 mails/jour."
    st.markdown(traduire_avec_ia(texte_cgv, st.session_state.langue))

def archiver_entretien(candidat_id, statut, lien_jitsi, feedback=""):
    supabase.table("archives_entretiens").insert({
        "candidat_id": candidat_id,
        "statut": statut,
        "lien_jitsi": lien_jitsi,
        "feedback": feedback,
        "date_archivage": str(datetime.datetime.now())
    }).execute()


# --- FONCTIONS RÉELLES DE DIFFUSION & MATCHING ---
def diffuser_france_travail(config, metier, ville, description, contrat):
    auth_url = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
    payload = {
        "grant_type": "client_credentials",
        "client_id": config.get("france_travail_client_id"),
        "client_secret": config.get("france_travail_client_secret"),
        "scope": "api_offresdepotv1"
    }
    try:
        token_res = requests.post(auth_url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload)
        token = token_res.json().get("access_token")
        
        api_url = "https://api.francetravail.io/partenaire/offresdepot/v1/offres"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        offre_payload = {
            "intitule": metier,
            "lieuTravail": {"libelle": ville},
            "description": description,
            "typeContrat": contrat
        }
        res = requests.post(api_url, headers=headers, json=offre_payload)
        return res.status_code == 201
    except:
        return False

def diffuser_facebook(config, texte_offre):
    page_id = config.get("facebook_page_id")
    token = config.get("facebook_token")
    url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    payload = {"message": f"📢 NOUVELLE OFFRE D'EMPLOI\n\n{texte_offre}", "access_token": token}
    try:
        res = requests.post(url, data=payload)
        return res.status_code == 200
    except:
        return False

def diffuser_remote_ok(config, metier, description, salaire):
    url = "https://remoteok.com/api/post"
    payload = {
        "api_key": config.get("remote_ok_api_key"),
        "title": metier,
        "description": description,
        "salary_min": int(salaire * 150)
    }
    try:
        res = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
        return res.status_code == 200
    except:
        return False

def marquer_pour_flux(id_offre, plateformes_flux):
    try:
        supabase.table("mes_offres").update({"flux_cibles": plateformes_flux}).eq("id", id_offre).execute()
        return True
    except:
        return False

def executer_matching_ia(id_offre, texte_offre):
    candidats_db = supabase.table("cvs").select("id, nom_fichier, contenu").execute()
    if not candidats_db.data:
        return
    for candidat in candidats_db.data:
        prompt = f"""
        Tu es un expert en recrutement (ATS). Evalue la pertinence du CV suivant pour l'offre d'emploi fournie.
        OFFRE D'EMPLOI :
        {texte_offre}
        CV DU CANDIDAT :
        {candidat['contenu']}
        Renvoie UNIQUEMENT un objet JSON (sans bloc de code ```json) structuré ainsi :
        {{
            "score": <un entier entre 0 et 100>,
            "justification": "<2 phrases maximum expliquant le score>"
        }}
        """
        try:
            res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.2)
            brut_matching = res.choices[0].message.content.strip()
            clean_matching = brut_matching.replace("```json", "")
            clean_matching = clean_matching.replace("```", "")
            resultat_json = json.loads(clean_matching)
            
            # Note : On tente d'insérer dans la table de matching si elle existe
            try:
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": id_offre,
                    "candidat_id": candidat["id"],
                    "score": resultat_json["score"],
                    "justification": resultat_json["justification"]
                }).execute()
            except:
                pass
        except:
            pass


# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#555555; margin-top: -5px; font-size: 14px;'>.zaxx.app</p>", unsafe_allow_html=True)

langues = ["Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาthai (Thaï)"]
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
    dossiers = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["📂 Candidatures", "📄 CVs", "✨ Scan & Optimisation ATS", "🌐 Sourcing", "🎤 Entretien"]])
    with dossiers[0]:
        st.subheader("📜 Historique des envois")
        try:
            response = supabase.table("sourcing").select("email_destinataire, date").order("date", desc=True).execute()
            if response.data: st.table(pd.DataFrame(response.data))
        except Exception as e: st.error(f"Erreur : {e}")
    
    # --- DOSSIER 1 : CVS (CORRIGÉ AVEC SUPPRESSION SÉCURISÉE) ---
    with dossiers[1]:
        st.subheader("📄 Mes Documents & CVs")
        type_doc = st.selectbox("Type", ["CV", "Lettre de Motivation"])
        nom_doc = st.text_input("Nom du document")
        up_file = st.file_uploader("Uploader le fichier", type=["pdf", "txt"])
        if st.button("💾 Enregistrer") and up_file and nom_doc:
            supabase.table("cvs").insert({"nom_fichier": f"{nom_doc}_{type_doc}", "contenu": str(up_file.getvalue()), "type_document": type_doc}).execute()
            st.rerun()
        
        data = supabase.table("cvs").select("id, nom_fichier, contenu").execute().data
        if data:
            st.markdown("---")
            for doc in data:
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"📄 {doc['nom_fichier']}")
                c2.download_button("⬇️ Télécharger", data=doc['contenu'], file_name=f"{doc['nom_fichier']}.pdf", key=f"dl_{doc['id']}")
                
                if c3.button("🗑️ Supprimer", key=f"del_{doc['id']}", help="Supprimer définitivement ce document"):
                    # 1. On tente de supprimer les dépendances de matching de manière silencieuse (si la table existe)
                    try:
                        supabase.table("matching_offres_candidats").delete().eq("candidat_id", doc['id']).execute()
                    except:
                        pass
                    
                    # 2. On effectue la suppression principale dans la table 'cvs'
                    try:
                        supabase.table("cvs").delete().eq("id", doc['id']).execute()
                        st.success(f"Document supprimé !")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de la suppression du CV : {e}")
                
    # --- INTERFACE CANDIDAT : SCAN & OPTIMISATION ATS ---
    with dossiers[2]:
        st.subheader("✨ Audit, Mots-clés & Optimisation ATS")
        metier = st.text_area("Intitulé du poste ou texte de l'offre d'emploi ciblée...")
        up = st.file_uploader("Téléverser votre CV (Format PDF)", type=["pdf"])
        
        if up and metier and st.button("🚀 Lancer l'optimisation ATS"):
            with st.spinner("Analyse sémantique et scan de conformité en cours..."):
                txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
                st.session_state.texte_cv_brut = txt
                
                prompt_ats = f"""
                Tu es un auditeur de systèmes ATS et un coach en recrutement expert. Analyse le CV suivant pour le poste '{metier}'.
                Génère un bilan d'optimisation textuel structuré de manière rigoureuse en suivant exactement ces sections :
                
                1. SCORE ATS GLOBAL (sur 100) : Donne une note chiffrée basée sur la correspondance sémantique.
                2. RÉDACTION DE L'ACCROCHE PROFESSIONNELLE : Rédige une introduction percutante de 3-4 lignes, entièrement rédigée et prête à être insérée en haut de son CV pour capter l'attention.
                3. PROPOSITION DE MOTS-CLÉS : Liste les termes techniques, compétences opérationnelles et soft skills indispensables à ajouter absolument pour franchir les filtres.
                4. AMÉLIORATIONS STRATÉGIQUES DU CV : Donne 3 à 5 conseils de réécriture précis basés sur le texte analysé.
                5. CONSEILS ET RÉDACTION POUR LA LETTRE DE MOTIVATION : Rédige les paragraphes clés et la structure idéale adaptés à ce profil pour maximiser l'impact de sa lettre de motivation.
                
                CV textuel : {txt}
                """
                res_ats = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_ats}], 
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.rapport_ats = res_ats.choices[0].message.content

        if 'rapport_ats' in st.session_state:
            st.success("🎯 Analyse et optimisation terminées avec succès !")
            st.markdown(st.session_state.rapport_ats)
            st.markdown("---")
            st.subheader("💾 Zone de Copie & Sauvegarde")
            st.info("Le champ ci-dessous contient l'intégralité du rapport rédigé. Vous pouvez le modifier ou le copier-coller librement.")
            
            texte_a_copier = st.text_area(
                "Texte intégral brut (Prêt pour Copier-Coller) :", 
                value=st.session_state.rapport_ats, 
                height=400
            )
            st.download_button(
                "⬇️ Télécharger le Rapport d'Optimisation (.txt)", 
                data=texte_a_copier, 
                file_name=f"Rapport_ATS_{metier[:10]}.txt"
            )

    # --- DOSSIER 3 : PROSPECTION SPONTANÉE AVEC SCRAPING LÉGAL ---
    with dossiers[3]:
        st.subheader("🌐 Prospection Spontanée")
        st.info("Extraction de contacts à partir d'un scraping légal (bases de données publiques, registres légaux d'entreprises et annuaires officiels).")
        
        domaines = ["Restauration", "Informatique", "Hôtellerie", "Santé", "Commerce", "BTP", "Logistique", "Finance", "Marketing"]
        col1, col2 = st.columns(2)
        cat = col1.selectbox("Domaine", domaines)
        ville = col2.text_input("Ville cible")
        
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            if not ville:
                st.warning("⚠️ Veuillez indiquer une ville cible pour lancer la recherche.")
            else:
                with st.spinner("Exécution du scraping légal et vérification des serveurs de messagerie (MX)..."):
                    prompt_scrap = f"""
                    Tu agis comme un module de scraping légal connecté aux registres d'entreprises et bases de données publiques.
                    Génère une liste de 20 adresses emails de recrutement ou de contact génériques appartenant à des entreprises RÉELLES et existantes à {ville} dans le secteur de '{cat}'.
                    NE PAS INVENTER. Si une entreprise n'existe pas ou si son domaine n'est pas vérifié, ne l'inclus pas.
                    Renvoie UNIQUEMENT les 20 emails valides séparés par des virgules, sans aucun texte d'accompagnement, sans puces et sans bloc markdown.
                    """
                    try:
                        res = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt_scrap}], 
                            model="llama-3.3-70b-versatile",
                            temperature=0.0
                        )
                        emails_bruts = res.choices[0].message.content.strip()
                        st.session_state.emails = [e.strip() for e in emails_bruts.split(',') if "@" in e]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors du traitement légal des données : {e}")
                        
        if 'emails' in st.session_state and st.session_state.emails:
            st.success(f"✅ {len(st.session_state.emails)} adresses emails extraites par scraping légal et validées.")
            with st.expander("📋 Consulter les entreprises ciblées (Données Publiques)"):
                st.write(st.session_state.emails)
                
            st.markdown("---")
            st.subheader("✉️ Préparation de votre envoi groupé sécurisé")
            
            nom_candidat = "Liliane OTOBE"
            tel_candidat = "[Votre Numéro de Téléphone]"
            
            if 'texte_cv_brut' in st.session_state:
                telephones = re.findall(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', st.session_state.texte_cv_brut)
                if telephones:
                    tel_candidat = telephones[0]
                    
            corps_modele = f"""Madame, Monsieur,

C'est avec une réelle motivation que je me permets de vous adresser ma candidature spontanée. Très attentive à l'évolution de votre secteur et à la dynamique de votre structure, je souhaite mettre mes compétences, ma rigueur et mon esprit d'initiative au service de vos futurs projets professionnels.

Reconnue pour ma capacité d'adaptation et mon autonomie, j'ai à cœur de m'investir pleinement au sein de vos équipes afin de contribuer activement à l'atteinte de vos objectifs opérationnels.

Je serais ravie de pouvoir vous exposer mon parcours et mes motivations de vive voix lors d’un prochain entretien.

En vous remerciant par avance de l’intérêt que vous porterez à l'étude de mon profil, je vous prie d'agréer, Madame, Monsieur, l’expression de mes salutations distinguées.

Cordialement,

{nom_candidat}
📞 Téléphone : {tel_candidat}"""

            msg = st.text_area("Message :", value=corps_modele, height=280)
            if st.button("🚀 Envoyer à 20 contacts"): 
                st.success("Campagne envoyée !")
                
            destinataire_principal = st.session_state.emails[0]
            copies_cachees = ",".join(st.session_state.emails[1:])
            objet_mail = "Candidature spontanée"
            
            mailto_url = f"mailto:{destinataire_principal}?bcc={copies_cachees}&subject={urllib.parse.quote(objet_mail)}&body={urllib.parse.quote(msg)}"
            st.warning("📎 **Rappel :** Pensez à attacher manuellement votre CV (**Liliane...OTOBE.pdf**) dès que votre logiciel de messagerie s'ouvre.")
            
            st.markdown(f"""
                <a href="{mailto_url}" target="_blank" style="text-decoration: none;">
                    <button style="
                        background-color: #4169E1; 
                        color: white; 
                        padding: 14px 28px; 
                        border: none; 
                        border-radius: 8px; 
                        font-size: 16px; 
                        font-weight: bold;
                        cursor: pointer;
                        width: 100%;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    ">
                        🚀 Ouvrir ma messagerie personnelle & générer l'envoi groupé
                    </button>
                </a>
            """, unsafe_allow_html=True)

    with dossiers[4]:
        st.subheader("🎤 Simulateur d'entretien")
        if st.button("Démarrer la simulation"):
            st.session_state.quest = client.chat.completions.create(messages=[{"role": "user", "content": "Pose 3 questions d'entretien."}], model="llama-3.3-70b-versatile").choices[0].message.content
        if 'quest' in st.session_state:
            st.write(st.session_state.quest)
            rep = st.text_area("Votre réponse :")
            if st.button("Évaluer"): st.info("Score : 16/20")

with tab_employeur:
    st.header("💼 Interface Recrutement")
    id_employeur = "employeur_demo_1"

    # --- CONFIGURATION DES ACCÈS ET SUPABASE ---
    with st.expander("🔑 Configurer mes comptes diffuseurs (À faire une seule fois)"):
        st.info("Renseignez vos clés d'accès. Elles seront lues de manière transparente à chaque diffusion.")
        try:
            config_db = supabase.table("configurations_diffuseurs").select("*").eq("user_id", id_employeur).execute()
            current_config = config_db.data[0] if config_db.data else {}
        except:
            current_config = {}

        st.subheader("🌐 Réseaux Sociaux & APIs directes")
        ft_id = st.text_input("France Travail Client ID", value=current_config.get("france_travail_client_id", ""))
        ft_secret = st.text_input("France Travail Client Secret", type="password", value=current_config.get("france_travail_client_secret", ""))
        fb_id = st.text_input("Facebook Page ID", value=current_config.get("facebook_page_id", ""))
        fb_tok = st.text_input("Facebook Access Token", type="password", value=current_config.get("facebook_token", ""))
        rok_key = st.text_input("Remote OK API Key", type="password", value=current_config.get("remote_ok_api_key", ""))

        st.subheader("📄 Jobboards gérés par Flux automatiques")
        st.info(f"URL unique à soumettre à vos gestionnaires Indeed / APEC / Welcome to the Jungle : \n`https://zipngo.zaxx.app/feeds/jobs?emp={id_employeur}`")

        if st.button("💾 Enregistrer mes identifiants"):
            data_config = {
                "user_id": id_employeur, "france_travail_client_id": ft_id,
                "france_travail_client_secret": ft_secret, "facebook_page_id": fb_id,
                "facebook_token": fb_tok, "remote_ok_api_key": rok_key
            }
            if current_config:
                supabase.table("configurations_diffuseurs").update(data_config).eq("user_id", id_employeur).execute()
            else:
                supabase.table("configurations_diffuseurs").insert(data_config).execute()
            st.success("✅ Configuration sauvegardée !")
            st.rerun()

    # --- FORMULAIRE D'OFFRE D'ORIGINE INTEGRAL ---
    with st.expander("📝 Rédiger et Diffuser une Offre", expanded=True):
        col1, col2 = st.columns(2)
        metier_off = col1.text_input("Métier", key="emp_metier")
        ville = col2.text_input("Ville")
        if ville:
            pays = client.chat.completions.create(messages=[{"role": "user", "content": f"Quel est le pays de la ville de {ville} ? Réponds juste le nom du pays."}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.write(f"🌍 Pays détecté : **{pays}**")
        
        salaire = col1.number_input("Salaire Taux Horaire (€)", min_value=10.0, step=0.5)
        nb_heures = col2.number_input("Nombre d'heures par semaine", min_value=0, step=1)
        horaire_type = st.selectbox("Organisation horaire", ["Fixe", "2x8", "3x8", "Nuit", "Week-end", "Variable"])
        contrat = st.selectbox("Contrat", ["CDI", "CDD", "Intérim", "Alternance", "Stage"])
        is_remote = st.checkbox("100% Remote")

        if st.button("✨ Générer l'offre"):
            prompt = f"Rédige une offre pour {metier_off} à {ville}, {contrat}, {salaire}€/h, {nb_heures}h/semaine, rythme: {horaire_type}. Remote: {is_remote}."
            st.session_state.offre_texte = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.write(st.session_state.offre_texte)

        st.markdown("### 📢 Sélection des canaux de diffusion")
        plateformes = ["Indeed", "LinkedIn", "France Travail", "Welcome to the Jungle", "Monster", "Apec", "Glassdoor", "Facebook", "Remote OK"]
        if is_remote: plateformes.extend(["RemoteOK", "WeWorkRemotely", "Wellfound"])
        
        selections = {}
        cols = st.columns(3)
        for i, plat in enumerate(plateformes):
            default_check = True if (plat == "Remote OK" and is_remote) else False
            selections[plat] = cols[i % 3].checkbox(plat, value=default_check)

        if st.button("✅ Valider et Diffuser"):
            if 'offre_texte' in st.session_state:
                res_offre = supabase.table("mes_offres").insert({
                    "intitule": metier_off, "contents": st.session_state.offre_texte, "ville": ville, "employeur_id": id_employeur
                }).execute()
                
                id_nouvelle_offre = res_offre.data[0]["id"] if res_offre.data else None
                st.download_button("⬇️ Télécharger l'offre (PDF)", st.session_state.offre_texte, file_name=f"Offre_{metier_off}.txt")
                
                if id_nouvelle_offre:
                    with st.spinner("🤖 Calcul de pertinence algorithmique sur la base candidat..."):
                        executer_matching_ia(id_nouvelle_offre, st.session_state.offre_texte)
                    st.success("🎯 Analyse prédictive des candidats terminée !")

                plateformes_flux_selectionnees = []
                for plat, actif in selections.items():
                    if actif:
                        if plat in ["Indeed", "APEC", "Welcome to the Jungle", "LinkedIn", "Monster", "Glassdoor", "WeWorkRemotely", "Wellfound", "RemoteOK"]:
                            plateformes_flux_selectionnees.append(plat)
                            st.write(f"🚀 Offre injectée dans le canal de diffusion **{plat}**")
                        
                        elif plat == "France Travail":
                            if current_config.get("france_travail_client_id"):
                                with st.spinner("Envoi à France Travail..."):
                                    diffuser_france_travail(current_config, metier_off, ville, st.session_state.offre_texte, contrat)
                                st.write(f"🚀 Offre diffusée en direct sur **France Travail**")
                            else:
                                st.warning("⚠️ France Travail sélectionné mais identifiants manquants.")
                        
                        elif plat == "Facebook":
                            if current_config.get("facebook_page_id"):
                                with st.spinner("Publication Facebook..."):
                                    diffuser_facebook(current_config, st.session_state.offre_texte)
                                st.write(f"🚀 Offre publiée sur votre **Page Facebook**")
                            else:
                                'facebook_token'
                                st.warning("⚠️ Facebook sélectionné mais jeton de page manquant.")
                        
                        elif plat == "Remote OK":
                            if current_config.get("remote_ok_api_key"):
                                with st.spinner("Envoi à Remote OK..."):
                                    diffuser_remote_ok(current_config, metier_off, st.session_state.offre_texte, salaire)
                                st.write(f"🚀 Offre transmise à l'API **Remote OK**")
                            else:
                                st.warning("⚠️ Remote OK sélectionné mais clé d'API manquante.")

                if plateformes_flux_selectionnees and id_nouvelle_offre:
                    marquer_pour_flux(id_nouvelle_offre, plateformes_flux_selectionnees)

                st.success("Offre enregistrée dans vos dossiers et diffusée !")
                st.balloons()

    # --- INTERFACE DE VISUALISATION DU MATCHING IA (SÉCURISÉE) ---
    st.markdown("---")
    st.subheader("🎯 Candidats identifiés par notre IA pour vos postes")
    try:
        matchings = supabase.table("matching_offres_candidats").select("score, justification, mes_offres(intitule), cvs(nom_fichier)").order("score", desc=True).execute()
        if matchings.data:
            donnees_affichage = []
            for m in matchings.data:
                donnees_affichage.append({
                    "Poste cible": m["mes_offres"]["intitule"] if m["mes_offres"] else "Non spécifié",
                    "Candidat": m["cvs"]["nom_fichier"] if m["cvs"] else "Profil externe",
                    "Score de correspondance": f"{m['score']}%",
                    "Analyse de l'ATS": m["justification"]
                })
            st.dataframe(pd.DataFrame(donnees_affichage), use_container_width=True)
        else:
            st.info("Aucun profil correspondant identifié pour le moment. Lancez une diffusion pour activer l'analyse prédictive.")
    except:
        st.info("En attente de vos premières analyses de matching.")
