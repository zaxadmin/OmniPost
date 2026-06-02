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


# --- FONCTIONS D'ORIGINE & ARCHIVAGE ---
def afficher_cgv():
    texte_cgv = "1. Accès Candidat 6€/3mois | Recruteur 39€/mois. 2. Limites Gratuit : 1 CV/mois, 1 campagne/mois. 3. Premium : 3 CVs/semaine, 20 mails/jour."
    st.markdown(traduire_avec_ia(texte_cgv, st.session_state.langue))

def archiver_entretien(candidat_id, statut, lien_jitsi, feedback=""):
    try:
        supabase.table("archives_entretiens").insert({
            "candidat_id": candidat_id,
            "statut": statut,
            "lien_jitsi": lien_jitsi,
            "feedback": feedback,
            "date_archivage": str(datetime.datetime.now())
        }).execute()
    except:
        pass


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

def diffuser_remote_ok(config, metier, description, sala):
    url = "https://remoteok.com/api/post"
    payload = {
        "api_key": config.get("remote_ok_api_key"),
        "title": metier,
        "description": description,
        "salary_min": int(sala * 150)
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
            clean_matching = brut_matching.replace("
```json", "").replace("```", "")
            resultat_json = json.loads(clean_matching)
            
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
    
    # --- INTERFACE CANDIDAT : CVS ---
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
                    try: supabase.table("matching_offres_candidats").delete().eq("candidat_id", doc['id']).execute()
                    except: pass
                    try:
                        supabase.table("cvs").delete().eq("id", doc['id']).execute()
                        st.success(f"Document supprimé !")
                        st.rerun()
                    except Exception as e: st.error(f"Erreur lors de la suppression du CV : {e}")
                
    # --- INTERFACE CANDIDAT : SCAN & OPTIMISATION ATS ---
    with dossiers[2]:
        st.subheader("✨ Audit, Mots-clés & Optimisation ATS")
        metier = st.text_area("Intitulé du poste ou texte de l'offre d'emploi ciblée...", key="ats_metier")
        up = st.file_uploader("Téléverser votre CV (Format PDF)", type=["pdf"], key="ats_file")
        
        if up and metier and st.button("🚀 Lancer l'optimisation ATS"):
            with st.spinner("Analyse sémantique et scan de conformité en cours..."):
                txt = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up.getvalue())).pages])
                st.session_state.texte_cv_brut = txt
                
                prompt_ats = f"Analyse le CV textuel suivant pour le poste '{metier}' et génère un bilan complet avec score, accroche, mots-clés et conseils pour la lettre de motivation. CV : {txt}"
                res_ats = client.chat.completions.create(messages=[{"role": "user", "content": prompt_ats}], model="llama-3.3-70b-versatile")
                st.session_state.rapport_ats = res_ats.choices[0].message.content

        if 'rapport_ats' in st.session_state:
            st.success("🎯 Analyse et optimisation terminées avec succès !")
            st.markdown(st.session_state.rapport_ats)
            st.markdown("---")
            texte_a_copier = st.text_area("Texte intégral brut (Prêt pour Copier-Coller) :", value=st.session_state.rapport_ats, height=300)
            st.download_button("⬇️ Télécharger le Rapport (.txt)", data=texte_a_copier, file_name="Rapport_ATS.txt")

    # --- INTERFACE CANDIDAT : SOURCING ---
    with dossiers[3]:
        st.subheader("🌐 Prospection Spontanée")
        domaines = ["Restauration", "Informatique", "Hôtellerie", "Santé", "Commerce", "BTP", "Logistique", "Finance", "Marketing"]
        col1, col2 = st.columns(2)
        cat = col1.selectbox("Domaine", domaines)
        ville_source = col2.text_input("Ville cible", key="source_ville")
        
        if st.button("🔍 Rechercher 20 nouveaux contacts"):
            if not ville_source: st.warning("⚠️ Veuillez indiquer une ville.")
            else:
                with st.spinner("Scraping légal en cours..."):
                    prompt_scrap = f"Génère une liste de 20 adresses emails de recrutement ou de contact génériques appartenant à des entreprises RÉELLES et existantes à {ville_source} dans le secteur de '{cat}'. Sépare par des virgules uniquement."
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt_scrap}], model="llama-3.3-70b-versatile")
                    st.session_state.emails = [e.strip() for e in res.choices[0].message.content.split(',') if "@" in e]
                    st.rerun()
                        
        if 'emails' in st.session_state and st.session_state.emails:
            st.write(st.session_state.emails)
            msg = st.text_area("Message :", value="Madame, Monsieur, ...", height=150)
            mailto_url = f"mailto:{st.session_state.emails[0]}?bcc={','.join(st.session_state.emails[1:])}&subject=Candidature&body={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{mailto_url}" target="_blank"><button style="background-color: #4169E1; color: white; padding: 12px; border: none; border-radius: 8px; width: 100%;">🚀 Ouvrir ma messagerie</button></a>', unsafe_allow_html=True)

    # --- INTERFACE CANDIDAT : INTERACTION ET ARCHIVES ENTRETIENS ---
    with dossiers[4]:
        st.subheader("🎤 Mon Espace Entretiens (Validations & Archives)")
        
        # Action : Le candidat valide une heure proposée par l'employeur
        try:
            entretiens_proposes = supabase.table("archives_entretiens").select("*").eq("statut", "Proposé").execute().data
            if entretiens_proposes:
                st.info("💡 Vous avez des invitations à un entretien en attente de votre validation :")
                for ent in entretiens_proposes:
                    st.markdown(f"**Planifié pour le :** {ent['date_entretien']}")
                    choix_horaire = st.radio("Choisissez votre créneau horaire :", json.loads(ent['horaires_proposes']), key=f"horaire_{ent['id']}")
                    if st.button("✅ Confirmer cet horaire", key=f"conf_{ent['id']}"):
                        final_datetime = f"{ent['date_entretien']} à {choix_horaire}"
                        supabase.table("archives_entretiens").update({
                            "statut": "Confirmé",
                            "heure_validee": choix_horaire,
                            "date_entretien": final_datetime
                        }).eq("id", ent['id']).execute()
                        st.success("Entretien validé et confirmé !")
                        st.rerun()
                    st.markdown("---")
        except: pass

        # Affichage des différentes archives (À venir vs Passés)
        t_avenir, t_passes = st.tabs(["🕒 Entretiens à venir", "📜 Historique & Archives passées"])
        
        with t_avenir:
            try:
                data_futurs = supabase.table("archives_entretiens").select("*").eq("statut", "Confirmé").execute().data
                if data_futurs:
                    for ent in data_futurs:
                        col_a, col_b = st.columns([3, 1])
                        col_a.markdown(f"📆 **Date & Heure :** {ent['date_entretien']} | 🎥 **Salon :** Jitsi")
                        col_b.markdown(f'<a href="{ent["lien_jitsi"]}" target="_blank"><button style="background-color: #22c55e; color: white; border: none; padding: 6px 12px; border-radius: 5px;">Rejoindre Jitsi</button></a>', unsafe_allow_html=True)
                        
                        # Option pour clore/archiver l'entretien après coup
                        feedback_txt = st.text_input("Ajouter des notes / feedback après l'entretien", key=f"feed_{ent['id']}")
                        if st.button("🗄️ Archiver l'entretien", key=f"arch_{ent['id']}"):
                            supabase.table("archives_entretiens").update({"statut": "Passé", "feedback": feedback_txt}).eq("id", ent['id']).execute()
                            st.rerun()
                        st.markdown("---")
                else: st.write("Aucun entretien programmé.")
            except: st.write("Aucun entretien programmé.")

        with t_passes:
            try:
                data_passes = supabase.table("archives_entretiens").select("*").eq("statut", "Passé").execute().data
                if data_passes: st.dataframe(pd.DataFrame(data_passes), use_container_width=True)
                else: st.write("Aucune archive disponible.")
            except: st.write("Aucune archive disponible.")


with tab_employeur:
    st.header("💼 Interface Recrutement")
    id_employeur = "employeur_demo_1"

    with st.expander("🔑 Configurer mes comptes diffuseurs"):
        try:
            config_db = supabase.table("configurations_diffuseurs").select("*").eq("user_id", id_employeur).execute()
            current_config = config_db.data[0] if config_db.data else {}
        except: current_config = {}
        ft_id = st.text_input("France Travail Client ID", value=current_config.get("france_travail_client_id", ""))
        ft_secret = st.text_input("France Travail Client Secret", type="password", value=current_config.get("france_travail_client_secret", ""))
        fb_id = st.text_input("Facebook Page ID", value=current_config.get("facebook_page_id", ""))
        fb_tok = st.text_input("Facebook Access Token", type="password", value=current_config.get("facebook_token", ""))
        rok_key = st.text_input("Remote OK API Key", type="password", value=current_config.get("remote_ok_api_key", ""))

        if st.button("💾 Enregistrer mes identifiants"):
            data_config = {"user_id": id_employeur, "france_travail_client_id": ft_id, "france_travail_client_secret": ft_secret, "facebook_page_id": fb_id, "facebook_token": fb_tok, "remote_ok_api_key": rok_key}
            if current_config: supabase.table("configurations_diffuseurs").update(data_config).eq("user_id", id_employeur).execute()
            else: supabase.table("configurations_diffuseurs").insert(data_config).execute()
            st.success("✅ Configuration sauvegardée !")
            st.rerun()

    # --- FORMULAIRE D'OFFRE ---
    with st.expander("📝 Rédiger et Diffuser une Offre", expanded=False):
        col1, col2 = st.columns(2)
        metier_off = col1.text_input("Métier", key="emp_metier")
        ville_off = col2.text_input("Ville", key="emp_ville")
        salaire = col1.number_input("Salaire Taux Horaire (€)", min_value=10.0, step=0.5)
        nb_heures = col2.number_input("Nombre d'heures par semaine", min_value=0, step=1)
        horaire_type = st.selectbox("Organisation horaire", ["Fixe", "2x8", "3x8", "Nuit", "Week-end", "Variable"])
        contrat = st.selectbox("Contrat", ["CDI", "CDD", "Intérim", "Alternance", "Stage"])
        is_remote = st.checkbox("100% Remote")

        if st.button("✨ Générer l'offre"):
            prompt = f"Rédige une offre pour {metier_off} à {ville_off}, {contrat}, {salaire}€/h."
            st.session_state.offre_texte = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile").choices[0].message.content
            st.write(st.session_state.offre_texte)

        if st.button("✅ Valider et Diffuser"):
            if 'offre_texte' in st.session_state:
                res_offre = supabase.table("mes_offres").insert({"intitule": metier_off, "contents": st.session_state.offre_texte, "ville": ville_off, "employeur_id": id_employeur}).execute()
                id_nouvelle_offre = res_offre.data[0]["id"] if res_offre.data else None
                if id_nouvelle_offre: executer_matching_ia(id_nouvelle_offre, st.session_state.offre_texte)
                st.success("Offre enregistrée et diffusée avec calcul de matching IA !")

    # --- LISTE CANDIDATS AVEC ACTION DE PLANIFICATION ENTRETIEN (POUCE VERT) ---
    st.markdown("---")
    st.subheader("🎯 Candidats identifiés par notre IA & Planification d'entretiens")
    try:
        matchings = supabase.table("matching_offres_candidats").select("id, score, justification, candidat_id, mes_offres(intitule), cvs(nom_fichier)").order("score", desc=True).execute().data
        if matchings:
            for m in matchings:
                c1, c2, c3 = st.columns([3, 2, 2])
                c1.markdown(f"👤 **{m['cvs']['nom_fichier']}** -> Poste : *{m['mes_offres']['intitule']}*  \n🔥 Score : **{m['score']}%**")
                c2.info(m['justification'])
                
                # Le pouce déclenche le formulaire de proposition d'entretien
                if c3.button("👍 Retenir & Planifier Entretien", key=f"thumb_{m['id']}"):
                    st.session_state[f"planif_active_{m['id']}"] = True
                
                if st.session_state.get(f"planif_active_{m['id']}", False):
                    with st.form(key=f"form_rdv_{m['id']}"):
                        st.write("📆 **Proposer un rendez-vous au candidat**")
                        date_sel = st.date_input("Choisir la date", datetime.date.today())
                        
                        st.write("Proposez 3 horaires libres (ex: 10:00, 14:30) :")
                        h1 = st.text_input("Horaire option 1", "09:30")
                        h2 = st.text_input("Horaire option 2", "14:00")
                        h3 = st.text_input("Horaire option 3", "16:30")
                        
                        if st.form_submit_button("🚀 Envoyer l'invitation"):
                            room_name = f"zipngo-{m['candidat_id']}-{int(datetime.datetime.now().timestamp())}"
                            lien_jitsi = f"[https://meet.jit.si/](https://meet.jit.si/){room_name}"
                            
                            supabase.table("archives_entretiens").insert({
                                "candidat_id": m["candidat_id"],
                                "statut": "Proposé",
                                "lien_jitsi": lien_jitsi,
                                "date_entretien": str(date_sel),
                                "horaires_proposes": json.dumps([h1, h2, h3]),
                                "feedback": ""
                            }).execute()
                            
                            st.success("Invitation transmise avec succès au profil candidat !")
                            st.session_state[f"planif_active_{m['id']}"] = False
                            st.rerun()
                st.markdown("---")
        else: st.info("Aucun profil correspondant identifié pour le moment.")
    except Exception as e: st.info("En attente de vos premières analyses de matching.")
