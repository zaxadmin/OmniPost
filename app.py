import streamlit as st
import PyPDF2
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS (Texture 3D & Relief) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f2f6 0%, #ffffff 100%);
             background-image: linear-gradient(145deg, rgba(255,255,255,0.4) 10%, transparent 40%),
                               linear-gradient(145deg, rgba(0,0,0,0.05) 45%, transparent 55%); }
    .main .block-container { background-color: rgba(255, 255, 255, 0.85) !important; border-radius: 25px !important; box-shadow: 0 20px 40px rgba(0,0,0,0.1) !important; }
    .brand-title { font-size: 3rem; font-weight: 800; text-align: center; }
    .zip { color: #000080; } .ngo { color: #00FFFF; }
    .stButton>button { background-color: #007BFF !important; color: white !important; border-radius: 12px !important; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS ---
def creer_pdf_securise(contenu, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=contenu)
    return pdf.output(dest='S').encode('latin-1')

def executer_scrapping(is_premium):
    limite = 1000 if is_premium else 20
    return [f"Profil Candidat {i}" for i in range(1, limite + 1)]

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "profile_completed": False, "premium": False, "mode_remote": False})

# --- PAGE AUTHENTIFICATION ---
if not st.session_state.auth:
    langues = ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Nederlands", "中文", "日本語", "العربية", "Русский", "한국어", "हिन्दी", "Türkçe", "Polski", "Svenska", "Dansk", "Suomi", "Norsk", "Ελληνικά"]
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        st.selectbox("🌐", langues, label_visibility="collapsed")
    
    st.markdown("<div class='brand-title'><span class='zip'>zip</span><span class='ngo'>ngo</span> 👍</div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #000080;'>La mise en relation professionnelle qui place les compétences et la confidentialité au premier plan.</h3>", unsafe_allow_html=True)
    
    col_c, col_e = st.columns(2)
    with col_c:
        st.markdown("#### 👤 Pour les Candidats\n* **ATS :** Optimisation CV.\n* **Anonymat :** Propulsion sécurisée.\n* **Contrôle :** Consentement mutuel.")
    with col_e:
        st.markdown("#### 🏢 Pour les Employeurs\n* **Scrapping :** Ciblage intelligent.\n* **Dispatch :** Pays ou Remote.\n* **Agilité :** Visioconférence.")
    
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("✨ Entrer dans l'application"):
        st.session_state.auth = True
        st.session_state.user_type = role
        st.rerun()

# --- APPLICATION ---
elif not st.session_state.profile_completed:
    st.header(f"Mode d'emploi : {st.session_state.user_type}")
    if st.button("Valider et commencer"): st.session_state.profile_completed = True; st.rerun()

else:
    t = {"dash": "Tableau de bord", "label": "Profil/ATS", "scrap": "Scrapping", "match": "Entretiens", "cgv": "📜 CGV", "acc": "Mon Compte"}
    with st.sidebar:
        pays = st.selectbox("📍 Pays de recherche", ["France", "Belgique", "Suisse", "Canada", "Luxembourg", "Maroc", "Algérie", "Tunisie", "Sénégal", "Côte d'Ivoire", "Autre"])
        if st.checkbox("Activer Premium"): st.session_state.premium = True
        if st.session_state.premium: st.checkbox("🌍 Mode Remote (Illimité)", key="mode_remote")
        
        menu = st.radio("Navigation", list(t.values()))
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    if menu == t["dash"]:
        st.header("Tableau de bord")
        st.write(f"Recherche active en : **{pays}**")

    elif menu == t["label"]:
        st.header("Profil & ATS")
        cv = st.file_uploader("Déposer mon CV", type="pdf")
        mob = st.radio("Mobilité :", ["💼 Présentiel", "🌍 Remote"], horizontal=True)
        if cv and st.button("Optimiser"): st.success("CV analysé et optimisé.")

    elif menu == t["scrap"]:
        st.header("Scrapping & Dispatch")
        limite = 1000 if st.session_state.mode_remote else 20
        if st.button(f"🔍 Lancer Scrapping (Limite : {limite})"):
            st.write(executer_scrapping(st.session_state.premium))

    elif menu == t["match"]:
        if st.session_state.user_type == "Employeur":
            if st.button("👍 Valider"): st.session_state.pouce_employeur = True
        else:
            if st.button("👍 Accepter"): st.session_state.pouce_candidat = True
        
        if st.session_state.get("pouce_employeur") and st.session_state.get("pouce_candidat"):
            st.success("Match ! Anonymat levé.")
            st.link_button("🎥 Rejoindre la salle", "https://meet.jit.si/zipngo")
            if st.button("🔄 Réactiver l'anonymat"):
                st.session_state.pouce_employeur = False
                st.session_state.pouce_candidat = False
                st.rerun()

    elif menu == t["acc"]:
        st.markdown('<a href="mailto:creationsites06@gmail.com">📧 Support</a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
