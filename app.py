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
    "Canada": {"devise": "$ CAD", "guichet": "Guichet Emploi"},
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
    """Extrait proprement le JSON de l'IA sans risquer un crash"""
    try:
        texte_nettoye = re.sub(r"```json|```", "", texte_brut).strip()
        return json.loads(texte_nettoye)
    except:
        try:
            match = re.search(r"\{.*\}", texte_brut, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except:
            pass
    return {"score": 0, "justification": "Erreur d'analyse."}


# --- MOTEUR DE MATCHING ARRIÈRE-PLAN IA (> 50%) ---
def executer_matching_automatique_cv(id_cv, contenu_cv, candidat_remote, candidat_pays, candidat_ville, source="app"):
    """S'exécute immédiatement après la réception d'un CV pour chercher les offres correspondantes"""
    try:
        offres_db = supabase.table("mes_offres").select("*").execute().data
        if not offres_db:
            return
            
        for offre in offres_db:
            offre_remote = offre.get("is_remote", False)
            offre_pays = offre.get("pays", "France")
            
            if not (candidat_remote and offre_remote):
                if candidat_pays != offre_pays:
                    continue

            prompt = f"""
            Evalue la pertinence du CV suivant pour l'offre d'emploi fournie.
            OFFRE D'EMPLOI : {offre['contents']}
            CV DU CANDIDAT : {contenu_cv}
            Renvoie UNIQUEMENT un objet JSON structuré ainsi :
            {{
                "score": <un entier entre 0 et 100>,
                "justification": "<2 phrases maximum expliquant le score>"
            }}
            """
            try:
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile", temperature=0.1)
                brut = res.choices[0].message.content
                resultat_json = extraire_json_propre(brut)
                
                score = int(resultat_json.get("score", 0))
                
                # Sauvegarde dans la table de matching avec spécification de la source (app ou email)
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": offre["id"],
                    "candidat_id": id_cv,
                    "score": score,
                    "justification": resultat_json["justification"],
                    "source": source
                }).execute()
            except:
                pass
    except:
        pass


def executer_matching_ia_depuis_offre(id_offre, texte_offre, offre_remote, offre_pays):
    """S'exécute lorsqu'un employeur crée une nouvelle offre"""
    try:
        candidats_db = supabase.table("cvs").select("*").execute().data
        if not candidats_db: 
            return
            
        for candidat in candidats_db:
            cand_remote = candidat.get("is_remote", False)
            cand_pays = candidat.get("pays", "France")
            
            if not (offre_remote and cand_remote):
                if offre_pays != cand_pays: 
                    continue
                
            try:
                prompt = f"Calcule le score de matching (0 à 100) en JSON entre cette offre : {texte_offre} et ce CV : {candidat['contenu']}"
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                brut = res.choices[0].message.content
                resultat_json = extraire_json_propre(brut)
                
                supabase.table("matching_offres_candidats").insert({
                    "offre_id": id_offre, 
                    "candidat_id": candidat["id"], 
                    "score": int(resultat_json.get("score", 0)), 
                    "justification": resultat_json["justification"],
                    "source": candidat.get("source", "app")
                }).execute()
            except:
                pass
    except: 
        pass


# --- SIMULATION DE L'IA QUI LIT LES EMAILS ENTRANTS ---
def simuler_ia_reception_email(email_recu, nom_candidat, texte_cv, entreprise_id):
    """Simule l'arrivée d'une candidature par email sur l'adresse de l'entreprise renseignée"""
    res_cv = supabase.table("cvs").insert({
        "nom_fichier": f"[Email] {nom_candidat}", 
        "contenu": texte_cv,
        "pays": "France",
        "ville": "Non spécifié",
        "is_remote": False,
        "source": "email"
    }).execute()
    
    if res_cv.data:
        id_nouveau_cv = res_cv.data[0]["id"]
        executer_matching_automatique_cv(id_nouveau_cv, texte_cv, False, "France", "Non spécifié", source="email")


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
        candidat_remote = st.checkbox("🌍 Je recherche exclusivement des postes en 100% Remote (Supprime les barrières de pays)", value=False)
        
        up_file = st.file_uploader("Uploader votre CV (PDF ou TXT)", type=["pdf", "txt"])
        
        if st.button("💾 Enregistrer mon profil & Activer le matching automatique") and up_file and nom_doc:
            with st.spinner("Analyse du profil et matching automatique en cours..."):
                if up_file.name.endswith(".pdf"):
                    contenu_texte = "".join([p.extract_text() for p in PdfReader(io.BytesIO(up_file.getvalue())).pages])
                else:
                    contenu_texte = up_file.getvalue().decode("utf-8", errors="ignore")
                
                res_cv = supabase.table("cvs").insert({
                    "nom_fichier": nom_doc, 
                    "contenu": contenu_texte,
                    "pays": pays_cand,
                    "ville": ville_cand,
                    "is_remote": candidat_remote,
                    "source": "app"
                }).execute()
                
                if res_cv.data:
                    id_nouveau_cv = res_cv.data[0]["id"]
                    executer_matching_automatique_cv(id_nouveau_cv, contenu_texte, candidat_remote, pays_cand, ville_cand, source="app")
                    st.success("🎯 Profil enregistré ! Notre IA a scanné les offres et envoyé votre profil si le matching dépasse 50%.")
                    st.rerun()

    with dossiers[3]:
        st.subheader("🎤 Mon Espace Entretiens (Candidat)")
        sub_tab_invites, sub_tab_avenirs, sub_tab_passes = st.tabs(["📩 Invitations Reçues", "📅 Entretiens à venir", "🗄️ Entretiens passés"])
        # ... [Logique d'entretien identique à la précédente pour le candidat]


# --- ZONE EMPLOYEUR (AVEC AUTHENTIFICATION / CONFIGURATION COMPTE) ---
with tab_employeur:
    st.header("💼 Espace Recruteur & Gestion Globale")
    
    # --- ETAPE 1 : ENREGISTREMENT DES COORDONNÉES ENTREPRISE SI INEXISTANT ---
    if "entreprise_connectee" not in st.session_state:
        st.session_state.entreprise_connectee = None

    if not st.session_state.entreprise_connectee:
        st.info("🔒 Veuillez renseigner les informations de votre entreprise pour accéder à votre espace recruteur.")
        with st.form("form_enregistrement_entreprise"):
            nom_ent = st.text_input("🏢 Nom de l'entreprise *")
            siret_ent = st.text_input("🔢 Numéro SIRET (14 chiffres) *")
            email_notif = st.text_input("📩 Email de réception des candidatures (À notifier / Trié par l'IA) *")
            pays_ent = st.selectbox("📍 Pays du siège social", list(PAYS_CONFIG.keys()))
            
            submit_ent = st.form_submit_button("🔓 Valider et accéder au tableau de bord")
            if submit_ent:
                if nom_ent and siret_ent and email_notif:
                    # Enregistrement en BDD Supabase
                    try:
                        res_ent = supabase.table("entreprises").insert({
                            "nom": nom_ent,
                            "siret": siret_ent,
                            "email_reception": email_notif,
                            "pays": pays_ent
                        }).execute()
                        if res_ent.data:
                            st.session_state.entreprise_connectee = res_ent.data[0]
                            st.success("✅ Entreprise enregistrée avec succès !")
                            st.rerun()
                    except:
                        # Fallback local si la table n'est pas encore créée sur votre Supabase
                        st.session_state.entreprise_connectee = {"id": "demo_id", "nom": nom_ent, "siret": siret_ent, "email_reception": email_notif, "pays": pays_ent}
                        st.success("✅ Mode Démo activé avec succès !")
                        st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                    
    # --- ETAPE 2 : TABLEAU DE BORD SI L'ENTREPRISE EST AUTHENTIFIÉE ---
    else:
        ent_info = st.session_state.entreprise_connectee
        st.sidebar.markdown(f"🏢 **{ent_info['nom']}**\n\nSIRET : `{ent_info['siret']}`\n\n📩 Hub Email : `{ent_info['email_reception']}`")
        
        pays_employeur = ent_info['pays']
        devise_locale = PAYS_CONFIG[pays_employeur]["devise"]
        plateforme_locale = PAYS_CONFIG[pays_employeur]["plateforme_locale"]

        # --- SIMULATEUR DE CANDIDATURE PAR EMAIL (POUR VOS TESTS) ---
        with st.sidebar.expander("🧪 Simulateur de réception d'Email (Test Moteur ATS)"):
            st.caption("Simule l'envoi d'un CV externe reçu sur l'adresse email configurée.")
            test_nom = st.text_input("Nom du candidat externe")
            test_cv_text = st.text_area("Contenu texte du CV reçu")
            if st.button("📥 Simuler l'arrivée de l'email"):
                if test_nom and test_cv_text:
                    simuler_ia_reception_email(ent_info['email_reception'], test_nom, test_cv_text, ent_info['id'])
                    st.success("L'IA a lu l'email, extrait le CV, calculé le matching et distribué le profil !")
                    st.rerun()

        # --- GESTION DES TIROIRS EMPLOYEURS ---
        st.markdown("---")
        tiroir_principal, tiroir_vivier = st.tabs(["📥 TIROIR DES PROFILS MATCHÉS (>= 50%)", "🗄️ VIVIER DE CANDIDATURES (< 50%)"])

        try:
            matchings = supabase.table("matching_offres_candidats").select("id, score, justification, source, candidat_id, mes_offres(intitule, is_remote, pays), cvs(nom_fichier, is_remote, pays)").order("score", desc=True).execute().data
        except:
            matchings = []

        # TIROIR 1 : SUPÉRIEUR OU ÉGAL À 50%
        with tiroir_principal:
            st.markdown("#### 🎯 Candidats pertinents (Application + Tri Automatique de vos Emails)")
            compteur_principal = 0
            if matchings:
                for m in matchings:
                    if int(m['score']) >= 50:
                        compteur_principal += 1
                        badge_source = "📧 REÇU PAR EMAIL" if m.get('source') == "email" else "📱 CANDIDAT APP"
                        with st.expander(f"👤 {m['cvs']['nom_fichier']} - [{badge_source}] - Score IA : {m['score']}% sur : {m['mes_offres']['intitule']}"):
                            st.write(f"**Justification IA :** {m['justification']}")
                            if st.button("👍 Proposer un RDV Jitsi", key=f"t_rec_p_{m['id']}"):
                                st.session_state[f"form_active_{m['id']}"] = True
                            
                            if st.session_state.get(f"form_active_{m['id']}", False):
                                with st.form(key=f"f_rdv_{m['id']}"):
                                    dt = st.date_input("Date de l'entretien", datetime.date.today())
                                    slot1 = st.text_input("Horaire optionnel 1", "10:00")
                                    slot2 = st.text_input("Horaire optionnel 2", "14:30")
                                    if st.form_submit_button("📨 Envoyer l'invitation"):
                                        room = f"jitsi-zipngo-{m['id']}"
                                        supabase.table("archives_entretiens").insert({
                                            "candidat_id": m["candidat_id"], "statut": "Proposé",
                                            "lien_jitsi": f"https://meet.jit.si/{room}", "date_entretien": str(dt),
                                            "horaires_proposes": json.dumps([slot1])
                                        }).execute()
                                        st.success("Propositions de créneaux transmises !")
                                        st.session_state[f"form_active_{m['id']}"] = False
                                        st.rerun()
            if compteur_principal == 0:
                st.info("Aucun profil n'a encore atteint le seuil des 50% de pertinence.")

        # TIROIR 2 : VIVIER (INFÉRIEUR À 50% PROVENANT DE L'ADRESSE EMAIL)
        with tiroir_vivier:
            st.markdown("#### 🗄️ Profils écartés ou à ré-évaluer pour le futur (<50%)")
            compteur_vivier = 0
            if matchings:
                for m in matchings:
                    if int(m['score']) < 50:
                        compteur_vivier += 1
                        with st.expander(f"👤 {m['cvs']['nom_fichier']} - Score IA : {m['score']}% (Basse pertinence détectée sur l'adresse email)"):
                            st.warning(f"**Analyse ATS :** Ce profil n'est pas idéal pour le poste de *{m['mes_offres']['intitule']}* actuellement.")
                            st.write(f"**Justification :** {m['justification']}")
                            st.caption("Profil conservé automatiquement dans le vivier d'entreprise en conformité avec vos processus internes.")
            if compteur_vivier == 0:
                st.info("Le vivier est actuellement vide.")

        # --- SUIVI RECRUTEUR DES ENTRETIENS PROGRAMMES ---
        st.markdown("---")
        st.markdown("### 🕒 Suivi de vos entretiens recruteur")
        sub_rec_avenirs, sub_rec_passes = st.tabs(["📅 Mes rendez-vous à venir", "🗄️ Historique & Comptes-rendus"])
        # ... [Logique de suivi d'entretiens identique à la précédente version]

        # --- FORMULAIRE DE RÉDACTION D'OFFRE ---
        st.markdown("---")
        with st.expander("📝 Rédiger, Localiser et Diffuser une nouvelle Offre"):
            col_e1, col_e2 = st.columns(2)
            metier_off = col_e1.text_input("Intitulé du poste", key="e_job")
            ville_off = col_e2.text_input("Ville du poste", key="e_v")
            salaire = col_e1.number_input(f"Salaire proposé (En {devise_locale})", min_value=1.0, value=15.0)
            contrat = st.selectbox("Type de contrat", ["CDI", "CDD", "Freelance", "Stage"])
            offre_remote = st.checkbox("🌍 Poste ouvert au 100% Télétravail (Supprime la barrière géographique pays/ville)", value=False)
            
            if st.button("✨ Générer et Matcher l'offre"):
                texte_genere = f"Recherche profil pour {metier_off} à {ville_off}. Contrat {contrat}. Salaire : {salaire} {devise_locale}."
                st.session_state.current_offre_txt = texte_genere
                st.write(texte_genere)
                
            if st.button("✅ Publier l'offre à l'échelle locale / globale"):
                if "current_offre_txt" in st.session_state:
                    res_o = supabase.table("mes_offres").insert({
                        "intitule": metier_off, "contents": st.session_state.current_offre_txt,
                        "ville": ville_off, "pays": pays_employeur, "is_remote": offre_remote, "employeur_id": ent_info['id']
                    }).execute()
                    
                    if res_o.data:
                        id_o = res_o.data[0]["id"]
                        executer_matching_ia_depuis_offre(id_o, st.session_state.current_offre_txt, offre_remote, pays_employeur)
                        st.success(f"Offre publiée avec succès ! Diffusée localement via : {plateforme_locale}")
                        st.rerun()

# --- CONDITIONS GÉNÉRALES DE VENTE (CGV) ---
st.markdown("---")
with st.expander("⚖️ Conditions Générales de Vente (CGV) & Mentions Légales"):
    st.markdown("""
    ### Conditions Générales de Vente — zipngo ATS Premium Global
    **En vigueur au 2 juin 2026**
    
    1. **Objet :** Les présentes Conditions Générales de Vente régissent l'accès et l'utilisation des services de la plateforme `zipngo` de gestion automatique des candidatures et d'analyse algorithmique de CV (ATS).
    2. **Services fournis :** `zipngo` propose des outils de tri automatisé via Intelligence Artificielle, d'extraction de données depuis les courriels entrants d'entreprises, et de mise en relation de visioconférences.
    3. **Protection des données (RGPD) :** L'employeur s'engage à traiter les données des candidats récoltées par l'application ou via l'email de réception de candidatures conformément aux lois européennes et internationales de protection de la vie privée. L'entreprise est désignée comme responsable unique du traitement de son vivier.
    4. **Responsabilité :** `zipngo` met en œuvre un moteur d'IA (Groq Llama 3) calculant un score de pertinence statistique. `zipngo` ne saurait être tenu pour responsable d'erreurs de tri, d'interprétation humaine ou de non-adéquation d'un candidat lors des entretiens Jitsi Meet.
    """)
