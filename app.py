import streamlit as st
from supabase import create_client
from streamlit_javascript import st_javascript
from ai_engine import coach_ia, generate_offer, analyze_matching
from fpdf import FPDF

# 1. CONNEXION SUPABASE (Projet OP-)
supabase = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

# 2. DÉTECTION IA LOCALE VIA JS
has_local_ai = st_javascript("""
    async function check() {
        return (window.ai && (await window.ai.canCreateTextSession()) === "readily");
    }
    return await check();
""")

# 3. DONNÉES DES LANGUES (20)
LANGS = {
    "Français 🇫🇷": "Français", "English 🇺🇸": "English", "Malagasy 🇲🇬": "Malagasy",
    "Español 🇪🇸": "Español", "Deutsch 🇩🇪": "Deutsch", "Italiano 🇮🇹": "Italiano",
    "Português 🇧🇷": "Português", "Русский 🇷🇺": "Русский", "日本語 🇯🇵": "Japanese",
    "한국어 🇰🇷": "Korean", "العربية 🇸🇦": "Arabic", "हिन्दी 🇮🇳": "Hindi",
    "Türkçe 🇹🇷": "Turkish", "Polski 🇵🇱": "Polish", "Tiếng Việt 🇻🇳": "Vietnamese",
    "ไทย 🇹🇭": "Thai", "Nederlands 🇳🇱": "Dutch", "Svenska 🇸🇪": "Swedish",
    "Bahasa 🇮🇩": "Indonesian", "Ελληνικά 🇬🇷": "Greek"
}

# 4. PARAMÈTRES
is_candidat = st.query_params.get("view") == "candidat"
user_email = st.query_params.get("user", "invite@zaxx.app")

# SIDEBAR COMMUNE
with st.sidebar:
    st.title("Zaxx.app")
    sel_lang = st.selectbox("🌐 Langue", list(LANGS.keys()))
    lang_name = LANGS[sel_lang]
    if has_local_ai: st.success("🚀 IA Native active")

if is_candidat:
    # ================= VUE CANDIDAT =================
    st.title(f"🚀 Espace Candidat ({lang_name})")
    menu = st.tabs(["📊 Dashboard", "🪄 Coach IA", "📁 Mon Tiroir"])

    with menu[0]:
        st.subheader("Suivi")
        res = supabase.table("candidatures").select("*").eq("email_candidat", user_email).execute()
        for c in res.data:
            st.info(f"Poste: {c['poste_vise']} | Status: {c['status']}")

    with menu[1]:
        st.subheader("Optimisation")
        cv = st.text_area("Votre CV actuel")
        opt = st.selectbox("Action", ["Relooker", "Lettre", "Adapter"])
        ctx = st.text_input("Métier/Offre cible") if opt != "Relooker" else ""
        if st.button("Lancer l'IA"):
            key = "relook" if "Relooker" in opt else ("lettre" if "Lettre" in opt else "adapt")
            res_ia = coach_ia(cv, key, ctx, lang_name)
            st.session_state.doc = res_ia
            st.markdown(res_ia)
            if st.button("💾 Sauvegarder"):
                supabase.table("tiroir_documents").insert({"user_email":user_email, "type_doc":opt, "contenu":res_ia}).execute()

    with menu[2]:
        st.subheader("Mes Documents")
        docs = supabase.table("tiroir_documents").select("*").eq("user_email", user_email).execute()
        for d in docs.data:
            with st.expander(f"{d['type_doc']} - {d['date_creation']}"):
                st.write(d['contenu'])
                # Export PDF
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, txt=d['contenu'].encode('latin-1', 'ignore').decode('latin-1'))
                st.download_button("📥 PDF", pdf.output(dest='S'), file_name="zaxx.pdf")

else:
    # ================= VUE EMPLOYEUR =================
    st.title(f"💼 Dashboard Recruteur ({lang_name})")
    t1, t2 = st.tabs(["📢 Offres", "📂 Candidats"])
    
    with t1:
        titre = st.text_input("Poste")
        if st.button("🪄 Rédiger"):
            st.session_state.off = generate_offer(titre, lang_name)
        desc = st.text_area("Contenu", value=st.session_state.get('off',''))
        if st.button("Diffuser"):
            supabase.table("offres").insert({"titre":titre, "contenu":desc}).execute()

    with t2:
        st.subheader("Candidatures")
        cands = supabase.table("candidatures").select("*").execute()
        for cand in cands.data:
            c1, c2 = st.columns([3,1])
            c1.write(f"**{cand['nom_candidat']}** ({cand['score_matching']}%)")
            if c2.button("🟠 Pouce Orange", key=cand['id']):
                supabase.table("candidatures").update({"status":"valide"}).eq("id", cand['id']).execute()
                st.toast("Validé !")
