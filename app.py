import streamlit as st
import PyPDF2
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS ---
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

def executer_recherche(is_premium):
    limite = 1000 if is_premium else 20
    return [f"Profil Candidat {i}" for i in range(1, limite + 1)]

def ajouter_alerte(msg):
    if "alertes" not in st.session_state: st.session_state.alertes = []
    st.session_state.alertes.append(msg)

# --- INITIALISATION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "profile_completed": False, "premium": False, "mode_remote": False, "alertes": []})

# --- PAGE AUTHENTIFICATION ---
if not st.session_state.auth:
    col_lang, col_rest = st.columns([1, 4])
    with col_lang:
        st.selectbox("🌐", ["Français", "English", "Español", "Deutsch", "Italiano", "Português", "Nederlands", "中文", "日本語", "العربية", "Русский", "한국어", "हिन्दी", "Türkçe", "Polski", "Svenska", "Dansk", "Suomi", "Norsk", "Ελληνικά"], label_visibility="collapsed")
    
    st.markdown("<div class='brand-title'><span class='zip'>zip</span><span class='ngo'>ngo</span> 👍</div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #000080;'>La mise en relation professionnelle qui place les compétences et la confidentialité au premier plan.</h3>", unsafe_allow_html=True)
    
    col_c, col_e = st.columns(2)
    with col_c:
        st.markdown("#### 👤 Pour les Candidats\n* **Analyse :** Optimisation personnalisée.\n* **Anonymat :** Propulsion sécurisée.\n* **Contrôle :** Consentement mutuel.")
    with col_e:
        st.markdown("#### 🏢 Pour les Employeurs\n* **Recherche :** Ciblage des talents.\n* **Dispatch :** Pays ou Remote.\n* **Agilité :** Visioconférence intégrée.")
    
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
    t = {"dash": "Tableau de bord", "label": "Analyse Profil", "search": "Recherche Talents", "match": "Entretiens", "cgv": "📜 CGV", "acc": "Mon Compte"}
    with st.sidebar:
        st.markdown("**Statut :** <span style='color:green'>●</span> En ligne", unsafe_allow_html=True)
        pays = st.selectbox("📍 Pays de recherche", ["France", "Belgique", "Suisse", "Canada", "Luxembourg", "Maroc", "Algérie", "Tunisie", "Sénégal", "Côte d'Ivoire", "Autre"])
        if st.checkbox("Activer Premium"): st.session_state.premium = True
        if st.session_state.premium: st.checkbox("🌍 Mode Remote (Illimité)", key="mode_remote")
        
        # Affichage alertes
        if st.session_state.alertes:
            st.write("---")
            st.markdown("### 🔔 Vos notifications")
            for alerte in st.session_state.alertes: st.info(alerte)
            if st.button("Effacer tout"): st.session_state.alertes = []; st.rerun()
        
        menu = st.radio("Navigation", list(t.values()))
        if st.button("🚪 Déconnexion"): st.session_state.clear(); st.rerun()

    if menu == t["dash"]:
        st.header("Tableau de bord")
        st.write(f"Recherche active en : **{pays}**")

    elif menu == t["label"]:
        st.header("Analyse de Profil")
        cv = st.file_uploader("Déposer mon CV", type="pdf")
        if cv and st.button("Optimiser"): st.success("CV analysé et optimisé.")

    elif menu == t["search"]:
        st.header("Recherche Talents & Dispatch")
        limite = 1000 if st.session_state.mode_remote else 20
        if st.button(f"🔍 Lancer Recherche (Limite : {limite})"):
            st.write(executer_recherche(st.session_state.premium))

    elif menu == t["match"]:
        st.header("Gestion des Entretiens")
        if st.session_state.user_type == "Employeur":
            date = st.date_input("Date")
            h1 = st.time_input("Début")
            h2 = st.time_input("Fin")
            if st.button("Envoyer la proposition"):
                st.session_state.proposition = {"date": date, "debut": h1, "fin": h2}
                ajouter_alerte("Proposition envoyée au candidat.")
        else:
            if "proposition" in st.session_state:
                p = st.session_state.proposition
                st.info(f"📅 Proposition : {p['date']} à {p['debut']}")
                if st.button("✅ Accepter"): 
                    ajouter_alerte("Rendez-vous confirmé !")
                    st.link_button("🎥 Rejoindre la salle", "https://meet.jit.si/zipngo")
                if st.button("🔄 Proposer une autre heure"): ajouter_alerte("Contre-proposition envoyée.")

    elif menu == t["acc"]:
        st.header("Mon Compte")
        st.subheader("💡 Votre mode d'emploi")
        if st.session_state.user_type == "Candidat":
            st.info("1. Déposez votre CV. 2. Profil propulsé anonymement. 3. Validez les matchs et répondez aux RDV.")
        else:
            st.info("1. Recherchez des talents. 2. Marquez votre intérêt. 3. Proposez des créneaux et gérez les réponses.")
        st.markdown('<a href="mailto:creationsites06@gmail.com">📧 Support</a>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
