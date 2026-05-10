import streamlit as st
from supabase import create_client
from ai_engine import coach_ia, generate_offer, analyze_matching
from fpdf import FPDF
from datetime import datetime

# --- 1. CONFIGURATION & DICTIONNAIRE DES LANGUES ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="🚀", layout="wide")

LANGS = {
    "Français 🇫🇷": "Français", "English 🇺🇸": "English", "Malagasy 🇲🇬": "Malagasy", 
    "Español 🇪🇸": "Español", "Deutsch 🇩🇪": "Deutsch", "Italiano 🇮🇹": "Italiano", 
    "Português 🇧🇷": "Português", "Русский 🇷🇺": "Russian", "日本語 🇯🇵": "Japanese", 
    "العربية 🇸🇦": "Arabic", "Türkçe 🇹🇷": "Turkish", "Nederlands 🇳🇱": "Dutch",
    "한국어 🇰🇷": "Korean", "中文 🇨🇳": "Chinese", "हिन्दी 🇮🇳": "Hindi", 
    "Polski 🇵🇱": "Polish", "Svenska 🇸🇪": "Swedish", "Tiếng Việt 🇻🇳": "Vietnamese",
    "Bahasa Indonesia 🇮🇩": "Indonesian", "ไทย 🇹🇭": "Thai"
}

# --- 2. CONNEXIONS SUPABASE ---
# ZIP pour l'authentification / OP pour les données métier
supabase_auth = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
supabase_data = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

# --- 3. BARRE LATÉRALE ---
with st.sidebar:
    st.title("Zaxx.app")
    sel_lang = st.selectbox("🌐 Langue / Language", list(LANGS.keys()))
    lang_name = LANGS[sel_lang]
    if st.session_state.user:
        st.divider()
        st.write(f"👤 **{st.session_state.user}**")
        st.caption(f"Rôle : {st.session_state.role}")
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()

# --- 4. LOGIQUE D'ACCÈS (CONNEXION / INSCRIPTION) ---
if not st.session_state.user:
    st.header("Bienvenue sur Zipngo-Zaxx")
    tab_log, tab_reg = st.tabs(["Connexion", "Inscription"])
    
    with tab_reg:
        new_e = st.text_input("Email", key="reg_e")
        new_p = st.text_input("Mot de passe", type="password", key="reg_p")
        new_r = st.radio("Je suis un :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("S'inscrire"):
            try:
                supabase_auth.table("users").insert({"email": new_e, "password": new_p, "role": new_r}).execute()
                st.success("Compte créé sur ZIP ! Vous pouvez vous connecter.")
            except: st.error("Email déjà utilisé.")
            
    with tab_log:
        le = st.text_input("Email", key="log_e")
        lp = st.text_input("Mot de passe", type="password", key="log_p")
        if st.button("Entrer"):
            res = supabase_auth.table("users").select("*").eq("email", le).eq("password", lp).execute()
            if res.data:
                st.session_state.user = le
                st.session_state.role = res.data[0]['role']
                st.rerun()
            else: st.error("Identifiants invalides.")

else:
    # --- 5. INTERFACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        st.title(f"🚀 Espace Candidat ({lang_name})")
        tabs = st.tabs(["📊 Mes Entretiens", "🪄 Coach IA & ATS", "📁 Mon Tiroir"])
        
        with tabs[0]:
            st.subheader("Planification des entretiens")
            cands = supabase_data.table("candidatures").select("*").eq("email_candidat", st.session_state.user).execute()
            
            if not cands.data: 
                st.info("Aucune proposition pour le moment.")
            
            for c in cands.data:
                with st.expander(f"Poste : {c.get('poste_vise', 'Poste inconnu')}", expanded=True):
                    # Cas 1 : Le recruteur propose 2 dates
                    if c['status'] == 'attente_candidat':
                        st.warning("🔔 Le recruteur souhaite vous rencontrer ! Choisissez l'un des deux créneaux :")
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.write(f"📅 **Option A**")
                            st.write(f"{c['rdv_1_date']} à {c['rdv_1_heure']}")
                            if st.button("Choisir Option A", key=f"sel_a_{c['id']}"):
                                supabase_data.table("candidatures").update({
                                    "status": "valide",
                                    "rdv_final_date": c['rdv_1_date'],
                                    "rdv_final_heure": c['rdv_1_heure']
                                }).eq("id", c['id']).execute()
                                st.success("RDV Confirmé !")
                                st.rerun()
                                
                        with col_b:
                            st.write(f"📅 **Option B**")
                            st.write(f"{c['rdv_2_date']} à {c['rdv_2_heure']}")
                            if st.button("Choisir Option B", key=f"sel_b_{c['id']}"):
                                supabase_data.table("candidatures").update({
                                    "status": "valide",
                                    "rdv_final_date": c['rdv_2_date'],
                                    "rdv_final_heure": c['rdv_2_heure']
                                }).eq("id", c['id']).execute()
                                st.success("RDV Confirmé !")
                                st.rerun()

                    # Cas 2 : Le RDV est validé
                    elif c['status'] == 'valide':
                        st.success(f"🗓️ RDV Confirmé le {c['rdv_final_date']} à {c['rdv_final_heure']}")
                        st.link_button("🎥 Rejoindre le salon vidéo", f"https://meet.jit.si/Zaxx-Interview-{c['id']}")
                    
                    else:
                        st.info("⏳ Candidature en cours d'examen par le recruteur.")

        with tabs[1]:
            st.subheader("Optimisation de Profil IA")
            cv_text = st.text_area("Collez votre CV actuel", height=150)
            target = st.text_input("Poste visé")
            mode = st.selectbox("Action souhaitée", ["Relooker", "Passer l'ATS", "Lettre de Motivation"])
            if st.button("🪄 Lancer la magie Zaxx"):
                act = {"Relooker":"relook", "Passer l'ATS":"adapt", "Lettre de Motivation":"lettre"}
                st.session_state.res_ia = coach_ia(cv_text, act[mode], target, lang_name)
            
            if 'res_ia' in st.session_state:
                final_txt = st.text_area("Résultat IA", value=st.session_state.res_ia, height=250)
                if st.button("💾 Enregistrer dans mon Tiroir"):
                    supabase_data.table("tiroir_documents").insert({
                        "user_email": st.session_state.user, "type_doc": mode, "contenu": final_txt
                    }).execute()
                    st.success("Enregistré dans OmniPost !")

        with tabs[2]:
            st.subheader("📁 Mon Tiroir Personnel")
            docs = supabase_data.table("tiroir_documents").select("*").eq("user_email", st.session_state.user).execute()
            for d in docs.data:
                with st.expander(f"📄 {d['type_doc']} - {d['date_creation']}"):
                    st.write(d['contenu'])
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.multi_cell(0, 10, txt=d['contenu'].encode('latin-1', 'ignore').decode('latin-1'))
                    st.download_button("📥 PDF", pdf.output(dest='S'), file_name="zaxx_doc.pdf", key=f"dl_{d['id']}")

    # --- 6. INTERFACE EMPLOYEUR ---
    else:
        st.title(f"💼 Dashboard Recruteur ({lang_name})")
        t1, t2 = st.tabs(["📢 Publier une offre", "📂 Candidats & Planning"])
        
        with t1:
            p_title = st.text_input("Titre du poste")
            if st.button("🪄 Rédiger l'annonce"):
                st.session_state.off_gen = generate_offer(p_title, lang_name)
            p_desc = st.text_area("Contenu de l'offre", value=st.session_state.get('off_gen',''), height=250)
            if st.button("🚀 Publier sur Zaxx"):
                supabase_data.table("offres").insert({"titre": p_title, "contenu": p_desc, "recruteur_email": st.session_state.user}).execute()
                st.success("Offre publiée !")

        with t2:
            st.subheader("Gestion des entretiens")
            cands = supabase_data.table("candidatures").select("*").execute()
            for cand in cands.data:
                with st.expander(f"👤 {cand['nom_candidat']} (Score : {cand['score_matching']}%)"):
                    if cand['status'] == 'en_attente':
                        st.write("📅 **Proposer deux créneaux pour ce candidat :**")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.caption("Option 1")
                            d1 = st.date_input("Date A", key=f"d1_{cand['id']}")
                            h1 = st.time_input("Heure A", key=f"h1_{cand['id']}")
                        with c2:
                            st.caption("Option 2")
                            d2 = st.date_input("Date B", key=f"d2_{cand['id']}")
                            h2 = st.time_input("Heure B", key=f"h2_{cand['id']}")
                        
                        if st.button("🟠 Envoyer les propositions", key=f"send_{cand['id']}"):
                            supabase_data.table("candidatures").update({
                                "status": "attente_candidat",
                                "rdv_1_date": str(d1), "rdv_1_heure": str(h1),
                                "rdv_2_date": str(d2), "rdv_2_heure": str(h2)
                            }).eq("id", cand['id']).execute()
                            st.success("Invitations envoyées !")
                            st.rerun()
                    
                    elif cand['status'] == 'attente_candidat':
                        st.info("⏳ En attente de la confirmation du candidat.")
                    
                    elif cand['status'] == 'valide':
                        st.success(f"✅ RDV Confirmé : {cand['rdv_final_date']} à {cand['rdv_final_heure']}")
                        st.link_button("🎥 Entrer en Vidéo", f"https://meet.jit.si/Zaxx-Interview-{cand['id']}")
