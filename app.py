import streamlit as st
from supabase import create_client
from ai_engine import coach_ia, generate_offer, analyze_matching
from fpdf import FPDF

# --- CONNEXIONS SUPABASE ---
# Utilise les secrets ZIP pour l'auth et OP pour les données
supabase_auth = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
supabase_data = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="Zaxx.app", page_icon="🚀", layout="wide")

# Liste des 20 langues (simplifiée ici pour le code)
LANGS = {"Français 🇫🇷": "Français", "English 🇺🇸": "English", "Malagasy 🇲🇬": "Malagasy", "Español 🇪🇸": "Español", "Deutsch 🇩🇪": "Deutsch"}

# --- INITIALISATION SESSION ---
if 'user' not in st.session_state: st.session_state.user = None
if 'role' not in st.session_state: st.session_state.role = None

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("Zaxx.app")
    sel_lang = st.selectbox("🌐 Langue / Language", list(LANGS.keys()))
    lang_name = LANGS[sel_lang]
    if st.session_state.user:
        st.write(f"👤 Connecté : **{st.session_state.user}**")
        if st.button("Se déconnecter"):
            st.session_state.user = None
            st.rerun()

# --- LOGIQUE D'AFFICHAGE ---
if not st.session_state.user:
    st.header("Bienvenue sur Zaxx")
    t1, t2 = st.tabs(["Connexion", "Créer un compte"])
    
    with t2:
        e = st.text_input("Email", key="reg_e")
        p = st.text_input("Mot de passe", type="password", key="reg_p")
        r = st.radio("Vous êtes :", ["Candidat", "Employeur"])
        if st.button("S'inscrire"):
            supabase_auth.table("users").insert({"email": e, "password": p, "role": r}).execute()
            st.success("Compte créé avec succès !")
            
    with t1:
        le = st.text_input("Email", key="log_e")
        lp = st.text_input("Mot de passe", type="password", key="log_p")
        if st.button("Se connecter"):
            res = supabase_auth.table("users").select("*").eq("email", le).eq("password", lp).execute()
            if res.data:
                st.session_state.user = le
                st.session_state.role = res.data[0]['role']
                st.rerun()
            else: st.error("Identifiants incorrects.")

else:
    # --- INTERFACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        st.title(f"🚀 Mon Espace Zaxx ({lang_name})")
        menu = st.tabs(["📊 Entretiens Vidéo", "🪄 Coach IA & ATS", "📁 Mon Tiroir"])

        with menu[0]:
            st.subheader("Suivi des candidatures")
            res = supabase_data.table("candidatures").select("*").eq("email_candidat", st.session_state.user).execute()
            if not res.data: st.info("Aucune candidature en cours.")
            for c in res.data:
                with st.expander(f"Offre : {c['poste_vise']}"):
                    if c['status'] == 'valide':
                        st.success("✅ Recruteur prêt !")
                        st.link_button("🎥 Rejoindre l'entretien privé", f"https://meet.jit.si/Zaxx-Meet-{c['id']}")
                    else: st.warning("⏳ Analyse en cours par le recruteur...")

        with menu[1]:
            st.subheader("Optimisation de Profil")
            cv = st.text_area("Collez votre CV ici", height=150)
            mode = st.selectbox("Action IA", ["Relooker (Impact)", "Lettre de Motivation", "Passer l'ATS (Mots-clés)"])
            target = st.text_input("Poste ou Offre visée")
            
            if st.button("🪄 Lancer l'IA"):
                act = "relook" if "Relooker" in mode else ("lettre" if "Lettre" in mode else "adapt")
                st.session_state.temp_cv = coach_ia(cv, act, target, lang_name)
            
            if 'temp_cv' in st.session_state:
                final = st.text_area("Résultat éditable", value=st.session_state.temp_cv, height=200)
                c1, c2 = st.columns(2)
                if c1.button("🔍 Vérifier conformité ATS"):
                    t = analyze_matching(final, target)
                    st.metric("Score ATS", f"{t['score']}%")
                    st.write(f"**Verdict :** {t['verdict']}")
                if c2.button("💾 Sauvegarder dans le Tiroir"):
                    supabase_data.table("tiroir_documents").insert({"user_email":st.session_state.user, "type_doc":mode, "contenu":final}).execute()
                    st.success("Document enregistré !")

        with menu[2]:
            st.subheader("Mes Documents & Exports PDF")
            docs = supabase_data.table("tiroir_documents").select("*").eq("user_email", st.session_state.user).execute()
            for d in docs.data:
                with st.expander(f"📄 {d['type_doc']} - {d['date_creation']}"):
                    temp = st.radio("Style PDF", ["Bleu Zaxx", "Noir Expert"], key=d['id'])
                    pdf = FPDF()
                    pdf.add_page()
                    col = (0,70,127) if "Bleu" in temp else (40,40,40)
                    pdf.set_fill_color(*col); pdf.rect(0,0,8,297,'F')
                    pdf.set_font("Arial",'B',14); pdf.set_text_color(*col); pdf.set_x(12); pdf.cell(0,10,d['type_doc'], ln=True)
                    pdf.set_font("Arial",'',10); pdf.set_text_color(0,0,0); pdf.set_x(12); pdf.multi_cell(0,7,d['contenu'].encode('latin-1','ignore').decode('latin-1'))
                    st.download_button("📥 Télécharger PDF", pdf.output(dest='S'), file_name="zaxx_doc.pdf", key=f"dl_{d['id']}")

    # --- INTERFACE EMPLOYEUR ---
    else:
        st.title(f"💼 Dashboard Recruteur ({lang_name})")
        t1, t2 = st.tabs(["📢 Diffuser une offre", "📂 Candidats & Sélection"])
        
        with t1:
            poste = st.text_input("Titre du poste à pourvoir")
            if st.button("🪄 Rédiger l'annonce avec l'IA"):
                st.session_state.off = generate_offer(poste, lang_name)
            desc = st.text_area("Contenu de l'offre", value=st.session_state.get('off',''), height=200)
            if st.button("🚀 Publier sur Zaxx"):
                supabase_data.table("offres").insert({"titre":poste, "contenu":desc}).execute()
                st.success("L'offre est maintenant visible par les candidats.")

        with t2:
            st.subheader("Candidats à évaluer")
            cands = supabase_data.table("candidatures").select("*").execute()
            for cand in cands.data:
                c1, c2, c3 = st.columns([2,1,1])
                c1.write(f"**{cand['nom_candidat']}** (Score IA: {cand['score_matching']}%)")
                if c2.button("🟠 Valider Profil", key=cand['id']):
                    supabase_data.table("candidatures").update({"status":"valide"}).eq("id", cand['id']).execute()
                    st.rerun()
                if cand['status'] == 'valide':
                    c3.link_button("🎥 Vidéo", f"https://meet.jit.si/Zaxx-Meet-{cand['id']}")
