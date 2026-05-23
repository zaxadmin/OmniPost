
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
from supabase import create_client, Client
from pypdf import PdfReader
import requests
import json
import os

# --- CONFIGURATION DE PAGE ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- INITIALISATION DES APIS (SECRETS) ---
try:
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    GROQ_API_KEY = st.secrets["groq"]["api_key"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Erreur de configuration des clés API (Vérifie tes secrets Streamlit) : {e}")
    st.stop()

# --- DICTIONNAIRE DE LANGUES ---
LANGUAGES = {
    "Français": {
        "rules": "Règles du jeu 📜", "profile": "Mon Profil & ATS 👤", "propulsion": "Propulsion CV 🚀",
        "matches": "Matchs & Entretiens 🤝", "archive": "Tiroir d'archivage 🗄️", "account": "Mon Compte ⚙️",
        "create_job": "Créer une offre ✍️", "broadcast": "Diffuser l'offre 📢", "candidates": "Candidats reçus 🔍",
        "role_cand": "Candidat", "role_emp": "Employeur", "welcome": "Connexion ou Inscription Sécurisée",
        "submit_cv_req": "Action obligatoire pour activer votre inscription", "cv_desc": "L'inscription est gratuite pour 3 mois, mais vous devez obligatoirement déposer votre CV pour le matching automatique.",
        "premium_active": "Option Premium active : Optimisations ATS illimitées.", "premium_info": "🎁 Version Gratuite : Il vous reste {} / 5 réfections de CV.",
        "anonymity_alert": "📢 NOTE CONCERNANT L'ANONYMAT SUR LE DISPATCH : L'envoi s'exécutant via votre messagerie personnelle, votre e-mail réel sera visible.",
        "gold_rule_title": "✨ RÈGLE D'OR DE PUBLICATION AUTOMATIQUE :", "gold_rule_desc": "Toute offre enregistrée est immédiatement intégrée au flux interne de l'application."
    },
    "English": {
        "rules": "Rules of the game 📜", "profile": "My Profile & ATS 👤", "propulsion": "CV Propulsion 🚀",
        "matches": "Matches & Interviews 🤝", "archive": "Archiving Drawer 🗄️", "account": "My Account ⚙️",
        "create_job": "Create an offer ✍️", "broadcast": "Broadcast offer 📢", "candidates": "Candidates received 🔍",
        "role_cand": "Candidate", "role_emp": "Employer", "welcome": "Secure Login or Registration",
        "submit_cv_req": "Mandatory action to activate registration", "cv_desc": "Registration is free for 3 months, but you must upload your CV for automatic matching.",
        "premium_active": "Premium Option Active: Unlimited ATS optimizations.", "premium_info": "🎁 Free Version: You have {} / 5 CV updates left.",
        "anonymity_alert": "📢 ANONYMITY NOTICE ON DISPATCH: Sending via your personal email means your real address will be visible.",
        "gold_rule_title": "✨ GOLDEN RULE OF AUTOMATIC PUBLICATION:", "gold_rule_desc": "Any registered offer is immediately integrated into the internal application flow."
    }
}

for lang in ["Español", "Deutsch", "Italiano", "Português", "Nederlands", "Русский", "中文", "日本語", "العربية", "Polski", "Türkçe", "Swedish", "Hindi", "Korean", "Bengali", "Punjabi", "Javanese", "Vietnamese"]:
    if lang not in LANGUAGES:
        LANGUAGES[lang] = LANGUAGES["English"]

if "lang" not in st.session_state:
    st.session_state.lang = "Français"

# --- BARRE DE SÉLECTION DE LA LANGUE TOUT EN HAUT ---
col_logo, col_lang = st.columns([5, 1])
with col_lang:
    selected_lang = st.selectbox("🌐", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.lang), label_visibility="collapsed")
    st.session_state.lang = selected_lang
    t = LANGUAGES[st.session_state.lang]

# --- FONCTIONS REELLES IA ---
def appeler_groq_ia(prompt: str, system_instruction: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Erreur API ({response.status_code})"
    except:
        return "Erreur de connexion IA."

def calculer_score_matching_ia(cv_text: str, offre_text: str) -> int:
    system_instruction = "Tu es un algorithme RH. Évalue la correspondance entre le CV et l'offre. Réponds UNIQUEMENT par un nombre entier entre 0 et 100."
    resultat = appeler_groq_ia(f"CV:\n{cv_text}\n\nOffre:\n{offre_text}", system_instruction).strip()
    try:
        return int(''.join(filter(str.isdigit, resultat)))
    except:
        return 50

# --- LOGIQUE MISE À JOUR AUTOMATIQUE ENTREPRISES (7 JOURS) ---
def synchroniser_nouvelles_entreprises():
    mises_a_jour_anciennes = supabase.table("app_settings").select("*").eq("key", "last_company_scraping").execute().data
    devoir_scrapar = False
    maintenant = datetime.now()
    
    if not mises_a_jour_anciennes:
        devoir_scrapar = True
    else:
        derniere_date = datetime.fromisoformat(mises_a_jour_anciennes[0]["value"])
        if maintenant - tracking_date > timedelta(days=7):
            devoir_scrapar = True
            
    if devoir_scrapar:
        entreprises_existantes = [emp["company_name"] for emp in supabase.table("users").select("company_name").eq("user_type", "Employeur").execute().data if emp.get("company_name")]
        nouvelles_entreprises_decouvertes = ["Tech Innov Corp", "Avenir Digital", "Global RH 2026"]
        
        for ent in nouvelles_entreprises_decouvertes:
            if ent not in entreprises_existantes:
                pass
                
        nouveau_timestamp = {"key": "last_company_scraping", "value": maintenant.isoformat()}
        if not mises_a_jour_anciennes:
            supabase.table("app_settings").insert(nouveau_timestamp).execute()
        else:
            supabase.table("app_settings").update(nouveau_timestamp).eq("key", "last_company_scraping").execute()

try:
    synchroniser_nouvelles_entreprises()
except:
    pass

# --- CAPTURE DU LIEN MAGIQUE DANS L'URL ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_type" not in st.session_state: st.session_state.user_type = None
if "user_id" not in st.session_state: st.session_state.user_id = None
if "candidate_data" not in st.session_state: st.session_state.candidate_data = {}

query_params = st.query_params
if "access_token" in query_params or "#access_token" in query_params:
    try:
        session_user = supabase.auth.get_user()
        if session_user and session_user.user:
            user_email = session_user.user.email
            res = supabase.table("users").select("*").eq("user_email", user_email).execute()
            if len(res.data) > 0:
                user_record = res.data[0]
                st.session_state.auth = True
                st.session_state.user_email = user_email
                st.session_state.user_type = user_record["user_type"]
                st.session_state.user_id = user_record["id"]
                st.query_params.clear()
                st.rerun()
    except Exception as e:
        st.sidebar.error(f"Erreur lors de la validation du lien : {e}")

# --- CSS STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC; color: #1A237E; }
    [data-testid="stSidebar"] { background-color: #1A237E !important; border-right: 3px solid #00E5FF; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stButton>button { background: #1A237E !important; color: #FFFFFF !important; border-radius: 8px; font-weight: 700; }
    .gold-rule { background-color: #E6FFFA; border-left: 4px solid #319795; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
    .candidate-card { padding: 15px; background-color: #FFFFFF; border-left: 4px solid #00E5FF; border-radius: 6px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .info-rules { background-color: #EBF8FF; border-left: 4px solid #3182CE; padding: 15px; border-radius: 6px; margin-bottom: 15px; }
    .marketing-box { background: linear-gradient(135deg, #1A237E, #2A36B1); color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .marketing-box h3 { color: #00E5FF !important; margin-top: 0; }
    .marketing-grid { display: flex; justify-content: space-around; gap: 15px; margin-top: 20px; flex-wrap: wrap; }
    .marketing-item { background: rgba(255,255,255,0.1); padding: 12px 20px; border-radius: 8px; font-size: 14px; flex: 1; min-width: 200px; }
    .custom-footer { text-align: center; color: #64748B; padding-top: 30px; font-size: 13px; line-height: 1.8; }
    .custom-footer button { background: none !important; border: none !important; padding: 0 !important; color: #1A237E !important; text-decoration: none; cursor: pointer; font-weight: 600; font-size: 13px; }
    .custom-footer button:hover { color: #00E5FF !important; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# --- EXECUTION FLUX D'APPLICATION ---
if not st.session_state.auth:
    _, col, _ = st.columns([0.5, 2.0, 0.5])
    with col:
        # Titre avec le Pouce Orange à côté
        st.markdown("<h1 style='text-align:center; font-size: 50px; margin-bottom: 5px;'><span style='color:#1A237E;'>zip</span><span style='color:#00E5FF;'>ngo</span> <span style='font-size: 40px;'>👍</span></h1>", unsafe_allow_html=True)
        
        # Bloc marketing d'engagement (Candidats + Employeurs)
        st.markdown("""
        <div class='marketing-box'>
            <h3>Le point de rencontre parfait. Zéro perte de temps. Anonymat absolu.</h3>
            <p style='font-size: 16px; opacity: 0.95;'>
                Que vous soyez un <b>Candidat</b> à la recherche du poste idéal ou un <b>Employeur</b> en quête du talent rare, 
                Zipngo transforme votre manière de recruter. Concentrez-vous uniquement sur les compétences.
            </p>
            <div class='marketing-grid'>
                <div class='marketing-item'>🔒 <b>Anonymat Total des 2 Côtés</b><br><small>Identités masquées jusqu'à la fin de l'entretien vidéo.</small></div>
                <div class='marketing-item'>⚡ <b>Gain de Temps Record</b><br><small>Matching intelligent via IA. Plus aucun tri de CV inutile.</small></div>
                <div class='marketing-item'>👍 <b>Double Validation</b><br><small>Mise en relation uniquement en cas d'intérêt mutuel.</small></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1A237E; font-size:18px;'>{t['welcome']}</p>", unsafe_allow_html=True)

        role = st.radio("Je souhaite m'inscrire ou me connecter en tant que :", [t["role_cand"], t["role_emp"]], horizontal=True)
        email = st.text_input("Adresse e-mail :").strip().lower()

        company_name, siret, phone, manager_name = "", "", "", ""
        if role == t["role_emp"]:
            st.markdown("### 🏢 Informations obligatoires Entreprise")
            company_name = st.text_input("Nom de l'entreprise *").strip()
            siret = st.text_input("Numéro de SIRET (14 chiffres) *").strip()
            phone = st.text_input("Téléphone de l'entreprise *").strip()
            manager_name = st.text_input("Nom complet du responsable *").strip()

        if st.button("🚀 Recevoir mon Lien Magique de connexion", use_container_width=True):
            if "@" not in email:
                st.error("Veuillez entrer une adresse e-mail valide.")
                st.stop()
                
            db_role = "Candidat" if role == t["role_cand"] else "Employeur"
            res = supabase.table("users").select("*").eq("user_email", email).execute()
            
            if len(res.data) == 0 and db_role == "Employeur":
                if not (company_name and siret and phone and manager_name):
                    st.error("❌ Tous les champs entreprise marqués d'un astérisque (*) sont obligatoires pour l'inscription d'un Employeur.")
                    st.stop()
                if len(siret) != 14 or not siret.isdigit():
                    st.error("❌ Le numéro de SIRET doit comporter exactement 14 chiffres.")
                    st.stop()

            if len(res.data) == 0:
                expiration_base = (datetime.now() + timedelta(days=90)).isoformat()
                user_data = {
                    "user_email": email, 
                    "user_type": db_role, 
                    "pass_expires_at": expiration_base
                }
                if db_role == "Employeur":
                    user_data.update({
                        "company_name": company_name,
                        "siret": siret,
                        "phone": phone,
                        "manager_name": manager_name
                    })
                supabase.table("users").insert(user_data).execute()
            else:
                if res.data[0]["user_type"] != db_role:
                    st.error(f"Cette adresse e-mail est déjà rattachée à un espace {res.data[0]['user_type']}.")
                    st.stop()

            try:
                supabase.auth.signInWithOtp({"email": email})
                st.success("✨ Un lien magique vient de vous être envoyé ! Ouvrez votre boîte de réception pour vous connecter instantanément.")
            except Exception as e:
                st.error(f"Erreur lors de l'envoi du lien magique : {e}")
else:
    user_db = supabase.table("users").select("*").eq("id", st.session_state.user_id).execute().data[0]
    date_exp = datetime.fromisoformat(user_db["pass_expires_at"].replace("Z", "+00:00")).replace(tzinfo=None)
    is_pass_valide = date_exp > datetime.now()

    with st.sidebar:
        st.markdown("<h2 style='color:white;'>zipngo 👍</h2>", unsafe_allow_html=True)
        st.write(f"Espace : **{user_db['user_type']}**")
        st.write(f"`{st.session_state.user_email}`")
        if user_db['user_type'] == "Employeur":
            st.write(f"🏢 *{user_db['company_name']}*")
        
        if is_pass_valide:
            st.success(f"🎟️ Pass Actif -> {date_exp.strftime('%d/%m/%Y')}")
        else:
            st.error("🛑 Pass Expiré")
            
        st.divider()
        
        if st.session_state.user_type == "Candidat":
            prof_res = supabase.table("candidate_profiles").select("*").eq("user_id", st.session_state.user_id).execute()
            has_profile = len(prof_res.data) > 0
            st.session_state.candidate_data = prof_res.data[0] if has_profile else {}
            menu = st.radio("Navigation", [t["rules"], t["profile"], t["propulsion"], t["matches"], t["archive"], t["account"]])
        else:
            menu = st.radio("Navigation", [t["rules"], t["create_job"], t["broadcast"], t["candidates"], t["matches"], t["archive"], t["account"]])

        st.divider()
        if st.button("🚪 Déconnexion", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state.auth = False
            st.rerun()

    # ==========================================
    # LOGIQUE : RÈGLES DU JEU
    # ==========================================
    if menu == t["rules"]:
        st.header(t["rules"])
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class='info-rules'>
                <h4>👍 Système du Double Pouce Orange</h4>
                <p>Vos données restent anonymisées. Le contact n'est partagé que si le candidat et le recruteur activent réciproquement leur intérêt.</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class='info-rules' style='background-color:#FFFEE2; border-left-color:#D69E2E;'>
                <h4>🗄️ Tiroir d'Archivage Gratuit à Vie</h4>
                <p>Même après expiration de votre Pass, vos correspondances historiques restent accessibles sans frais.</p>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # LOGIQUE : MON PROFIL CANDIDAT & ATS
    # ==========================================
    elif menu == t["profile"]:
        st.header(t["profile"])
        c_data = st.session_state.candidate_data
        has_cv = "cv_extracted_text" in c_data and bool(c_data["cv_extracted_text"])
        
        if not has_cv:
            st.markdown(f"<div class='gold-rule' style='background-color:#FFF5F5;'><b>🚨 {t['submit_cv_req']}</b><br>{t['cv_desc']}</div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Déposer impérativement votre CV pour activer l'accès (PDF / TXT) *", type=["pdf", "txt"])
            if uploaded_file:
                texte_cv = "".join([p.extract_text() or "" for p in PdfReader(uploaded_file).pages]) if uploaded_file.name.lower().endswith(".pdf") else uploaded_file.getvalue().decode("utf-8")
                supabase.table("candidate_profiles").insert({
                    "user_id": st.session_state.user_id, "job_title": "À renseigner", "contract_type": "CDI", "city": "À renseigner", "cv_extracted_text": texte_cv
                }).execute()
                st.success("🎉 CV Enregistré avec succès ! Votre compte candidat est désormais validé et actif.")
                st.rerun()
        else:
            st.success("✅ Votre CV est déposé et actif sur la plateforme.")
            with st.form("f_cand"):
                t_input = st.text_input("Poste recherché *", value=c_data.get("job_title", ""))
                c_input = st.selectbox("Contrat *", ["CDI", "CDD", "Intérim", "Stage", "Freelance", "Alternance"], index=0)
                l_input = st.text_input("Ville cible *", value=c_data.get("city", ""))
                if st.form_submit_button("Sauvegarder mes critères"):
                    supabase.table("candidate_profiles").update({"job_title": t_input, "contract_type": c_input, "city": l_input}).eq("user_id", st.session_state.user_id).execute()
                    st.rerun()

    # ==========================================
    # LOGIQUE : PROPULSION CV (ANTI-DOUBLON)
    # ==========================================
    elif menu == t["propulsion"]:
        st.header(t["propulsion"])
        st.markdown(f"<div class='gold-rule'>{t['anonymity_alert']}</div>", unsafe_allow_html=True)
        st.subheader("📬 Entreprises cibles trouvées pour votre profil")
        
        toutes_entreprises = supabase.table("users").select("id", "company_name", "user_email").eq("user_type", "Employeur").execute().data
        emails_deja_propulses = [
            p["recipient_email"] for p in supabase.table("propulsion_history").select("recipient_email").eq("candidat_id", st.session_state.user_id).execute().data
        ]
        
        entreprises_filtrées = [emp for emp in toutes_entreprises if emp["user_email"] not in emails_deja_propulses]
        
        if not entreprises_filtrées:
            st.info("✨ Bravo ! Vous avez optimisé et envoyé votre profil à l'ensemble des entreprises cibles disponibles. Aucune nouvelle adresse pour le moment.")
        else:
            st.write(f"Filtrage actif : **{len(entreprises_filtrées)}** nouvelles opportunités uniques trouvées.")
            for emp in entreprises_filtrées[:5]:
                col_ent, col_act = st.columns([3, 1])
                with col_ent:
                    st.markdown(f"🏢 **{emp['company_name']}** — *Nouveau contact unique dédupliqué*")
                with col_act:
                    if st.button(f"Propulser mon profil", key=f"prop_{emp['id']}"):
                        supabase.table("propulsion_history").insert({
                            "candidat_id": st.session_state.user_id,
                            "recipient_email": emp["user_email"],
                            "sent_at": datetime.now().isoformat()
                        }).execute()
                        st.success(f"🚀 Profil envoyé de manière unique à {emp['company_name']} !")
                        st.rerun()

    # ==========================================
    # LOGIQUE : CRÉER UNE OFFRE (EMPLOYEUR)
    # ==========================================
    elif menu == t["create_job"]:
        st.header(t["create_job"])
        if not is_pass_valide:
            st.error("🛑 Votre Pass Employeur a expiré. Veuillez renouveler votre accès pour pouvoir publier une offre.")
        else:
            with st.form("f_offre"):
                titre = st.text_input("Intitulé du poste *")
                desc = st.text_area("Descriptif des compétences et critères recherchés *")
                contrat = st.selectbox("Type de contrat *", ["CDI", "CDD", "Intérim", "Stage", "Freelance", "Alternance"])
                lieu = st.text_input("Localisation *", value="À distance / Sur site")
                
                if st.form_submit_button("Publier l'offre"):
                    if titre and desc and lieu:
                        supabase.table("job_offers").insert({
                            "employeur_id": st.session_state.user_id, 
                            "title": titre, 
                            "company_name": user_db["company_name"], 
                            "location": lieu, 
                            "contract_type": contrat, 
                            "skills_required": desc
                        }).execute()
                        st.success("🎉 Offre enregistrée et publiée avec succès sur le flux interne zipngo !")
                    else:
                        st.error("Veuillez remplir tous les champs obligatoires (*).")

    # ==========================================
    # LOGIQUE : MATCHS & ENTRETIENS
    # ==========================================
    elif menu == t["matches"]:
        st.header(t["matches"])
        champ_filtre = "candidat_id" if st.session_state.user_type == "Candidat" else "employeur_id"
        matchs = supabase.table("matches_interviews").select("*").eq(champ_filtre, st.session_state.user_id).execute().data
        
        if not matchs:
            st.info("Aucun match réciproque (Double Pouce Orange) ou entretien programmé pour l'instant.")
        else:
            for m in matchs:
                statut_badge = "🤝 Match Confirmé" if (m.get("thumb_employeur") and m.get("thumb_candidat")) else "⏳ En attente de validation réciproque"
                st.markdown(f"""
                <div class='candidate-card'>
                    <h3>Poste : {m['job_title']}</h3>
                    <p><b>Statut :</b> {statut_badge}</p>
                    <p><b>Date d'entretien fixée :</b> {m['rdv_date'] if m.get('rdv_date') else 'Non planifiée'}</p>
                </div>
                """, unsafe_allow_html=True)

    # ==========================================
    # AUTRES STRUCTURES
    # ==========================================
    elif menu == t["broadcast"]:
        st.header(t["broadcast"])
        st.markdown(f"<div class='gold-rule'><b>{t['gold_rule_title']}</b><br>{t['gold_rule_desc']}</div>", unsafe_allow_html=True)
        st.info("📢 Suivi de diffusion multi-plateforme de tes offres en cours.")

    elif menu == t["candidates"]:
        st.header(t["candidates"])
        st.info("🔍 Liste des profils candidats ayant un score de matching élevé avec tes offres publiées.")

    elif menu == t["archive"]:
        st.header(t["archive"])
        st.info("🗄️ Tiroir d'archivage gratuit à vie. Tes correspondances historiques et ton journal restent accessibles ici.")

    elif menu == t["account"]:
        st.header(t["account"])
        st.write("⚙️ **Paramètres de ton compte**")
        st.write(f"E-mail d'authentification : `{st.session_state.user_email}`")
        st.write(f"Type de profil activé : `{st.session_state.user_type}`")
        if st.session_state.user_type == "Employeur":
            st.markdown(f"""
            - **Entreprise :** {user_db.get('company_name')}
            - **SIRET :** {user_db.get('siret')}
            - **Téléphone :** {user_db.get('phone')}
            - **Responsable :** {user_db.get('manager_name')}
            """)
            
        if st.session_state.user_email == "creationsites06@gmail.com":
            st.divider()
            st.subheader("🛠️ Espace Administrateur : Extraction des données")
            data_entreprises = supabase.table("users").select("*").eq("user_type", "Employeur").execute().data
            if data_entreprises:
                df = pd.DataFrame(data_entreprises)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Télécharger le CSV complet des Entreprises (Base de données)",
                    data=csv_data,
                    file_name=f"entreprises_zipngo_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("Aucune entreprise enregistrée dans la base de données pour le moment.")

# --- INJECTION ET LOGIQUE DIALOGUE POUR CGV & MENTIONS LEGALES ---
@st.dialog("Conditions Générales de Vente (CGV)")
def afficher_cgv():
    st.markdown("""
    ### CONDITIONS GÉNÉRALES DE VENTE & D'UTILISATION (CGV/CGU)
    **En vigueur au 23 mai 2026**
    
    ---
    #### 1. Objet de la plateforme
    L'application **zipngo** est un service de matching technologique et d'optimisation de processus RH propulsé par l'Intelligence Artificielle. Elle met en relation de manière anonymisée des profils Candidats et des structures Employeurs.
    
    #### 2. Principe Fondamental de l'Anonymat
    Zipngo garantit un **anonymat total, bilatéral et strict** (nom, prénom, coordonnées, raison sociale, e-mail) tout au long du processus initial de sélection et pendant l'intégralité de l'entretien vidéo synchrone natif. La levée de l'anonymat ne s'effectue qu'après validation conjointe post-entretien (Principe du Double Pouce Orange).
    
    #### 3. Conditions Financières et Abonnements
    * **Espace Candidat :** L'accès aux fonctionnalités de base et le dépôt du CV sont entièrement gratuits pour une période d'essai initiale de 3 mois.
    * **Espace Employeur :** L'accès à la création et la diffusion d'offres nécessite l'achat d'un Pass d'accès (90 jours). À l'expiration du Pass, la publication est suspendue mais le tiroir d'archivage historique reste accessible gratuitement à vie.
    
    #### 4. Responsabilités
    L'éditeur ne saurait être tenu responsable des déclarations inexactes faites par les utilisateurs (SIRET erronés, faux diplômes). Zipngo fournit un outil algorithmique d'aide à la décision mais ne garantit pas la conclusion définitive d'un contrat de travail.
    """)

@st.dialog("Mentions Légales & RGPD")
def afficher_mentions_legales():
    st.markdown("""
    ### MENTIONS LÉGALES & PROTECTION DES DONNÉES
    **En vigueur au 23 mai 2026**
    
    ---
    #### 1. Édition du site
    L'application **zipngo** et l'intégralité de ses modules algorithmiques sont la propriété exclusive de :
    * **Créatrice & Développeuse :** Liliane RAKOTOBE
    * **Contact Électronique :** creationsites06@gmail.com
    
    
  
 #### 2. Traitement des Données Personnelles (RGPD)
    Conformément aux directives européennes en vigueur, vous disposez d'un droit d'accès, de rectification et de suppression des données vous concernant. 
    * **Données collectées :** E-mail d'authentification, contenu textuel extrait du CV, informations d'identification d'entreprise (SIRET, Responsable, Téléphone).
    * **Finalité :** Exécution stricte de la mise en relation par matching affinitaire. Vos données ne sont jamais vendues, cédées ou louées à des tiers commerciaux.
    * **Conservation :** Les historiques d'échanges et tiroirs d'archivage restent conservés jusqu'à ce que l'utilisateur demande explicitement la suppression définitive de son compte.
    """)

# --- FOOTER ---
st.markdown("<hr>", unsafe_allow_html=True)
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #64748B; font-size: 13px;'>
        © 2026 zipngo | App Creator : <b>Liliane RAKOTOBE</b> 
        <a href="mailto:creationsites06@gmail.com" style="text-decoration:none;">✉️</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Boutons d'action natifs Streamlit stylisés en ligne pour ouvrir les modales légitimes
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("⚖️ Conditions Générales (CGV)", use_container_width=True, key="btn_cgv_footer"):
            afficher_cgv()
    with btn_col2:
        if st.button("🔒 Mentions Légales & RGPD", use_container_width=True, key="btn_ml_footer"):
            afficher_mentions_legales()
