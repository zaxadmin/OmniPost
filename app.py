import streamlit as st
import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    h1 { color: #007BFF !important; }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 10px; }
    .stInfo { background-color: #e3f2fd; border-left: 5px solid #007BFF; }
    </style>
    """, unsafe_allow_html=True)

# --- DICTIONNAIRE 20 LANGUES ---
LANGUAGES = {
    "Français": {"label": "Profil & ATS", "welcome": "Bienvenue", "dash": "Tableau de bord", "prop": "Propulsion", "match": "Entretiens", "off": "Diffusion", "acc": "Mon Compte"},
    "English": {"label": "Profile & ATS", "welcome": "Welcome", "dash": "Dashboard", "prop": "Propulsion", "match": "Interviews", "off": "Dispatch", "acc": "Account"},
    "Español": {"label": "Perfil y ATS", "welcome": "Bienvenido", "dash": "Tablero", "prop": "Propulsión", "match": "Entrevistas", "off": "Ofertas", "acc": "Cuenta"},
    "Deutsch": {"label": "Profil & ATS", "welcome": "Willkommen", "dash": "Dashboard", "prop": "Propulsion", "match": "Interviews", "off": "Jobs", "acc": "Konto"},
    "Italiano": {"label": "Profilo & ATS", "welcome": "Benvenuto", "dash": "Dashboard", "prop": "Propulsione", "match": "Interviste", "off": "Offerte", "acc": "Account"},
    "Português": {"label": "Perfil & ATS", "welcome": "Bem-vindo", "dash": "Painel", "prop": "Propulsão", "match": "Entrevistas", "off": "Ofertas", "acc": "Conta"},
    "Nederlands": {"label": "Profiel & ATS", "welcome": "Welkom", "dash": "Dashboard", "prop": "Propulsie", "match": "Interviews", "off": "Jobs", "acc": "Account"},
    "Русский": {"label": "Профиль & ATS", "welcome": "Добро пожаловать", "dash": "Панель", "prop": "Продвижение", "match": "Интервью", "off": "Вакансии", "acc": "Аккаунт"},
    "中文": {"label": "个人资料 & ATS", "welcome": "欢迎", "dash": "仪表板", "prop": "简历推广", "match": "面试", "off": "职位", "acc": "账户"},
    "日本語": {"label": "プロフィール & ATS", "welcome": "ようこそ", "dash": "ダッシュボード", "prop": "CV推進", "match": "面接", "off": "求人", "acc": "アカウント"},
    "한국어": {"label": "프로필 & ATS", "welcome": "환영합니다", "dash": "대시보드", "prop": "CV 추진", "match": "면접", "off": "채용", "acc": "계정"},
    "العربية": {"label": "الملف الشخصي & ATS", "welcome": "أهلاً بك", "dash": "لوحة التحكم", "prop": "دفع", "match": "مقابلات", "off": "وظائف", "acc": "الحساب"},
    "Türkçe": {"label": "Profil & ATS", "welcome": "Hoş geldiniz", "dash": "Panel", "prop": "CV İtici Güç", "match": "Mülakatlar", "off": "İşler", "acc": "Hesap"},
    "Polski": {"label": "Profil & ATS", "welcome": "Witamy", "dash": "Pulpit", "prop": "Propulsja", "match": "Rozmowy", "off": "Oferty", "acc": "Konto"},
    "Svenska": {"label": "Profil & ATS", "welcome": "Välkommen", "dash": "Panel", "prop": "Propulsion", "match": "Intervjuer", "off": "Jobb", "acc": "Konto"},
    "Norsk": {"label": "Profil & ATS", "welcome": "Velkommen", "dash": "Dashbord", "prop": "Fremdrift", "match": "Intervjuer", "off": "Jobber", "acc": "Konto"},
    "Dansk": {"label": "Profil & ATS", "welcome": "Velkommen", "dash": "Instrumentbræt", "prop": "Fremdrift", "match": "Interviews", "off": "Job", "acc": "Konto"},
    "Suomi": {"label": "Profiili & ATS", "welcome": "Tervetuloa", "dash": "Kojelauta", "prop": "Propulsio", "match": "Haastattelut", "off": "Työt", "acc": "Tili"},
    "Ελληνικά": {"label": "Προφίλ & ATS", "welcome": "Καλώς ήρθατε", "dash": "Πίνακας ελέγχου", "prop": "Προώθηση", "match": "Συνεντεύξεις", "off": "Θέσεις", "acc": "Λογαριασμός"},
    "Tiếng Việt": {"label": "Hồ sơ & ATS", "welcome": "Chào mừng", "dash": "Bảng điều khiển", "prop": "Thúc đẩy", "match": "Phỏng vấn", "off": "Việc làm", "acc": "Tài khoản"}
}

# --- SÉLECTEUR LANGUE ---
col1, _ = st.columns([1, 10])
with col1:
    if "lang" not in st.session_state: st.session_state.lang = "Français"
    st.session_state.lang = st.selectbox("🌐", list(LANGUAGES.keys()))
t = LANGUAGES[st.session_state.lang]

st.title("zipngo 👍")

# --- AUTH & SESSION ---
if "auth" not in st.session_state: 
    st.session_state.update({"auth": False, "premium": False, "user_type": "Candidat", "created_at": datetime.date.today()})

if not st.session_state.auth:
    st.markdown(f"""
    <div style='background:#f8f9fa; padding:20px; border-radius:15px; border-left: 5px solid #007BFF;'>
    <h3>{t['welcome']}</h3>
    <p><b>L'application qui révolutionne le recrutement.</b><br>
    Votre identité reste confidentielle jusqu'à ce que vous décidiez de vous dévoiler.<br><br>
    🚀 <i>Testez gratuitement notre période d'essai. Le Premium débloque des opportunités illimitées.</i></p>
    </div>
    """, unsafe_allow_html=True)
    
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    email = st.text_input("E-mail (Connexion magique) :")
    if st.button("✨ Entrer dans l'application"):
        st.session_state.update({"auth": True, "user_email": email, "user_type": role})
        st.rerun()

else:
    # --- MISE EN VEILLE (3 MOIS) ---
    delta = datetime.date.today() - st.session_state.created_at
    is_active = st.session_state.premium or delta.days <= 90

    with st.sidebar:
        if not is_active: st.error("⚠️ Compte en veille (Période d'essai dépassée)")
        elif st.session_state.get("premium"): st.success("✨ Premium Actif")
        else: st.warning("⚠️ Période d'essai (Standard)")
        menu = st.radio("Navigation", [t["dash"], t["label"], t["prop"], t["match"], t["off"], t["acc"]])
        if st.button("🚪 Déconnexion"): st.session_state.auth = False; st.rerun()

    # --- DASHBOARD ---
    if menu == t["dash"]:
        st.header(t["dash"])
        if st.session_state.user_type == "Candidat":
            st.info("📖 **Guide du Candidat :** Optimisez votre CV avec l'IA, propulsez-le anonymement et gérez vos entretiens.")
        else:
            st.info("📖 **Guide de l'Employeur :** Diffusez anonymement, validez les matchs pour lever l'anonymat, et planifiez vos rencontres.")
    
    # --- PROFIL & ATS ---
    elif menu == t["label"]:
        st.header(t["label"])
        st.file_uploader("Déposer mon CV")
        is_remote_search = st.checkbox("🌍 Je cherche des postes en Remote")
        if st.button("✨ Optimiser avec l'IA"): st.write("✅ Score ATS : Passé de 45% à 88%.")

    # --- PROPULSION ---
    elif menu == t["prop"]:
        st.header(t["prop"])
        if st.button("🚀 Propulser ma candidature"): st.success("Candidature transmise. Identité protégée.")

    # --- ENTRETIENS ---
    elif menu == t["match"]:
        st.header(t["match"])
        col1, col2 = st.columns(2)
        with col1: date = st.date_input("Date proposée")
        with col2: heure = st.time_input("Heure proposée")
        if st.button("✅ Confirmer proposition"): st.write("Proposition envoyée.")
        st.markdown("---")
        st.write("🎥 **Entretien Vidéo sécurisé :**")
        st.link_button("Rejoindre la salle", "https://meet.jit.si/zipngo", type="primary")

    # --- DIFFUSION ---
    elif menu == t["off"]:
        st.header(t["off"])
        is_remote = st.checkbox("🌍 Offre en Remote (Lève les restrictions de pays)")
        if st.button("📢 Diffuser mon offre"): st.balloons(); st.success("Offre diffusée !")

    # --- MON COMPTE ---
    elif menu == t["acc"]:
        st.header(t["acc"])
        st.write("Statut : Anonymat actif.")
        with st.expander("⚖️ Mentions Légales"):
            st.write("zipngo est une plateforme de mise en relation. Nous ne sommes pas responsables de la véracité des informations des utilisateurs.")
        with st.expander("📜 CGV"):
            st.write("Accès Premium pour usage illimité. Mise en veille automatique après 90 jours pour les comptes standards.")
        st.link_button("📧 Support & Suppression", "mailto:creationsites06@gmail.com")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
