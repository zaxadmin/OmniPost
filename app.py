import streamlit as st
from supabase import create_client
from streamlit_javascript import st_javascript
from ai_engine import coach_ia, generate_offer, analyze_matching
from fpdf import FPDF

# 1. CONNEXION SUPABASE (Projet OP-)
supabase = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

# 2. DÉTECTION IA LOCALE (Optionnel)
has_local_ai = st_javascript("return (window.ai && (await window.ai.canCreateTextSession()) === 'readily');")

# 3. CONFIGURATION LANGUES (20)
LANGS = {"Français 🇫🇷": "Français", "English 🇺🇸": "English", "Malagasy 🇲🇬": "Malagasy", "Español 🇪🇸": "Español", "Deutsch 🇩🇪": "Deutsch", "Italiano 🇮🇹": "Italiano", "Português 🇧🇷": "Português", "Русский 🇷🇺": "Russian", "日本語 🇯🇵": "Japanese", "العربية 🇸🇦": "Arabic", "Türkçe 🇹🇷": "Turkish", "Nederlands 🇳🇱": "Dutch"}

is_candidat = st.query_params.get("view") == "candidat"
user_email = st.query_params.get("user", "invite@zaxx.app")

with st.sidebar:
    st.title("Zaxx.app")
    sel_lang = st.selectbox("🌐 Langue", list(LANGS.keys()))
    lang_name = LANGS[sel_lang]
    if has_local_ai: st.success("🚀 IA Native activée")

if is_candidat:
    # ================= VUE CANDIDAT =================
    st.title(f"🚀 Espace Candidat ({lang_name})")
    menu = st.tabs(["📊 Suivi & Vidéo", "🪄 Coach IA & ATS", "📁 Mon Tiroir"])

    with menu[0]:
        st.subheader("Mes Candidatures")
        res = supabase.table("candidatures").select("*").eq("email_candidat", user_email).execute()
        for c in res.data:
            with st.expander(f"Poste : {c['poste_vise']}"):
                if c['status'] == 'valide':
                    st.success("✅ Recruteur prêt ! Salon vidéo isolé activé.")
                    st.link_button("🎥 Entrer en entretien", f"https://meet.jit.si/Zaxx-Meet-{c['id']}")
                else: st.warning("⏳ Examen en cours...")

    with menu[1]:
        st.subheader("Optimisation ATS & Relooking")
        cv = st.text_area("Votre CV", height=150)
        mode = st.selectbox("Action", ["Relooker", "Lettre", "Passer l'ATS"])
        target = st.text_input("Métier ou Offre")
        
        if st.button("🪄 Transformer"):
            action = "relook" if mode == "Relooker" else ("lettre" if mode == "Lettre" else "adapt")
            st.session_state.temp_cv = coach_ia(cv, action, target, lang_name)
        
        if 'temp_cv' in st.session_state:
            final_txt = st.text_area("Résultat (Éditable)", value=st.session_state.temp_cv, height=200)
            col1, col2 = st.columns(2)
            if col1.button("🔍 Re-tester l'ATS"):
                test = analyze_matching(final_txt, target)
                st.metric("Score ATS", f"{test['score']}%")
                st.info(test['verdict'])
            if col2.button("💾 Sauvegarder"):
                supabase.table("tiroir_documents").insert({"user_email":user_email, "type_doc":mode, "contenu":final_txt}).execute()
                st.success("Sauvegardé !")

    with menu[2]:
        st.subheader("Mes Documents & Templates")
        docs = supabase.table("tiroir_documents").select("*").eq("user_email", user_email).execute()
        for d in docs.data:
            with st.expander(f"{d['type_doc']} - {d['date_creation']}"):
                temp = st.radio("Style", ["Bleu Moderne", "Noir Pro"], key=d['id'])
                pdf = FPDF()
                pdf.add_page()
                color = (0,70,127) if "Bleu" in temp else (50,50,50)
                pdf.set_fill_color(*color); pdf.rect(0,0,10,297,'F')
                pdf.set_font("Arial", 'B', 14); pdf.set_text_color(*color)
                pdf.set_x(15); pdf.cell(0,10, d['type_doc'].upper(), ln=True)
                pdf.set_font("Arial", '', 11); pdf.set_text_color(0,0,0)
                pdf.set_x(15); pdf.multi_cell(0,8, d['contenu'].encode('latin-1','ignore').decode('latin-1'))
                st.download_button("📥 PDF", pdf.output(dest='S'), file_name="zaxx.pdf", key=f"dl_{d['id']}")

else:
    # ================= VUE EMPLOYEUR =================
    st.title(f"💼 Dashboard Recruteur ({lang_name})")
    t1, t2 = st.tabs(["📢 Offres", "📂 Candidats"])
    with t1:
        poste = st.text_input("Titre")
        if st.button("🪄 Rédiger"): st.session_state.o = generate_offer(poste, lang_name)
        desc = st.text_area("Offre", value=st.session_state.get('o',''))
        if st.button("Publier"): supabase.table("offres").insert({"titre":poste, "contenu":desc}).execute()
    with t2:
        cands = supabase.table("candidatures").select("*").execute()
        for cand in cands.data:
            c1, c2, c3 = st.columns([2,1,1])
            c1.write(f"**{cand['nom_candidat']}** ({cand['score_matching']}%)")
            if c2.button("🟠 Valider", key=f"v_{cand['id']}"):
                supabase.table("candidatures").update({"status":"valide"}).eq("id", cand['id']).execute()
            if cand['status'] == 'valide':
                c3.link_button("🎥 Vidéo", f"https://meet.jit.si/Zaxx-Meet-{cand['id']}")
