import streamlit as st
from supabase import create_client
from streamlit_javascript import st_javascript
from ai_engine import coach_ia, generate_offer
from fpdf import FPDF

# 1. CONNEXION SUPABASE
supabase = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

# 2. DÉTECTION IA LOCALE
has_local_ai = st_javascript("return (window.ai && (await window.ai.canCreateTextSession()) === 'readily');")

# 3. LANGUES (20)
LANGS = {"Français 🇫🇷": "Français", "English 🇺🇸": "English", "Malagasy 🇲🇬": "Malagasy", "Español 🇪🇸": "Español", "Deutsch 🇩🇪": "Deutsch", "Italiano 🇮🇹": "Italiano", "Português 🇧🇷": "Português", "Русский 🇷🇺": "Русский", "日本語 🇯🇵": "Japanese", "한국어 🇰🇷": "Korean", "العربية 🇸🇦": "Arabic", "हिन्दी 🇮🇳": "Hindi", "Türkçe 🇹🇷": "Turkish", "Polski 🇵🇱": "Polish", "Tiếng Việt 🇻🇳": "Vietnamese", "ไทย 🇹🇭": "Thai", "Nederlands 🇳🇱": "Dutch", "Svenska 🇸🇪": "Swedish", "Bahasa 🇮🇩": "Indonesian", "Ελληνικά 🇬🇷": "Greek"}

is_candidat = st.query_params.get("view") == "candidat"
user_email = st.query_params.get("user", "invite@zaxx.app")

with st.sidebar:
    st.title("Zaxx.app")
    sel_lang = st.selectbox("🌐 Langue", list(LANGS.keys()))
    lang_name = LANGS[sel_lang]

if is_candidat:
    # ================= VUE CANDIDAT =================
    st.title(f"🚀 Espace Candidat ({lang_name})")
    menu = st.tabs(["📊 Mon Suivi & Vidéo", "🪄 Coach IA", "📁 Mon Tiroir"])

    with menu[0]:
        st.subheader("Candidatures et Entretiens")
        res = supabase.table("candidatures").select("*").eq("email_candidat", user_email).execute()
        for c in res.data:
            with st.expander(f"Offre : {c['poste_vise']}"):
                if c['status'] == 'valide':
                    st.success("🎯 Profil retenu !")
                    # SALON UNIQUE : On utilise l'ID de la candidature pour garantir l'isolation
                    room_id = f"Zaxx-Meeting-{c['id']}"
                    st.link_button("🎥 Rejoindre mon entretien privé", f"https://meet.jit.si/{room_id}")
                else:
                    st.warning("⏳ En cours d'analyse...")

    with menu[1]:
        st.subheader("Coach IA")
        cv = st.text_area("Collez votre CV")
        opt = st.selectbox("Action", ["Relooker", "Lettre", "Adapter"])
        ctx = st.text_input("Métier/Offre") if opt != "Relooker" else ""
        if st.button("Lancer"):
            res_ia = coach_ia(cv, opt, ctx, lang_name)
            st.session_state.doc = res_ia
            st.markdown(res_ia)
            if st.button("💾 Sauvegarder"):
                supabase.table("tiroir_documents").insert({"user_email":user_email, "type_doc":opt, "contenu":res_ia}).execute()

    with menu[2]:
        st.subheader("Tiroir")
        docs = supabase.table("tiroir_documents").select("*").eq("user_email", user_email).execute()
        for d in docs.data:
            with st.expander(f"{d['type_doc']} - {d['date_creation']}"):
                st.write(d['contenu'])
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, txt=d['contenu'].encode('latin-1', 'ignore').decode('latin-1'))
                st.download_button("📥 PDF", pdf.output(dest='S'), file_name="zaxx.pdf")

else:
    # ================= VUE EMPLOYEUR =================
    st.title(f"💼 Dashboard Recruteur ({lang_name})")
    t1, t2 = st.tabs(["📢 Créer une offre", "📂 Candidats & Vidéo"])
    
    with t1:
        titre = st.text_input("Titre du poste")
        if st.button("🪄 Rédiger"):
            st.session_state.off = generate_offer(titre, lang_name)
        desc = st.text_area("Contenu", value=st.session_state.get('off',''), height=200)
        if st.button("Publier"):
            supabase.table("offres").insert({"titre":titre, "contenu":desc}).execute()
            st.success("Offre en ligne !")

    with t2:
        st.subheader("Gestion des Candidats")
        # Ici l'employeur ne voit que les candidats qui ont postulé
        cands = supabase.table("candidatures").select("*").execute()
        for cand in cands.data:
            c1, c2, c3 = st.columns([2,1,1])
            c1.write(f"**{cand['nom_candidat']}**")
            if c2.button("🟠 Valider", key=f"v_{cand['id']}"):
                supabase.table("candidatures").update({"status":"valide"}).eq("id", cand['id']).execute()
                st.toast("Candidat validé !")
            
            # Le bouton vidéo n'apparaît que pour les candidats validés
            if cand['status'] == 'valide':
                room_id = f"Zaxx-Meeting-{cand['id']}"
                c3.link_button("🎥 Entrer", f"https://meet.jit.si/{room_id}")
