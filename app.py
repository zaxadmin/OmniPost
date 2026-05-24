import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo", layout="wide", page_icon="👍")

# --- INITIALISATION LANGUES ---
LANGUAGES = {
    "Français": {"label": "Profil & ATS", "welcome": "Bienvenue", "dash": "Tableau de bord", "prop": "Propulsion CV", "match": "Matchs & Entretiens", "off": "Offres & Dispatch", "acc": "Mon Compte"},
    "English": {"label": "Profile & ATS", "welcome": "Welcome", "dash": "Dashboard", "prop": "CV Propulsion", "match": "Matches & Interviews", "off": "Jobs & Dispatch", "acc": "Account"},
    "Español": {"label": "Perfil y ATS", "welcome": "Bienvenido", "dash": "Tablero", "prop": "Propulsión CV", "match": "Entrevistas", "off": "Ofertas & Envío", "acc": "Cuenta"},
    "Deutsch": {"label": "Profil & ATS", "welcome": "Willkommen", "dash": "Dashboard", "prop": "CV-Propulsion", "match": "Interviews", "off": "Jobs & Dispatch", "acc": "Konto"},
    "Italiano": {"label": "Profilo & ATS", "welcome": "Benvenuto", "dash": "Dashboard", "prop": "Propulsione CV", "match": "Interviste", "off": "Offerte & Invio", "acc": "Account"},
    "Português": {"label": "Perfil & ATS", "welcome": "Bem-vindo", "dash": "Painel", "prop": "Propulsão CV", "match": "Entrevistas", "off": "Ofertas & Envio", "acc": "Conta"},
    "Nederlands": {"label": "Profiel & ATS", "welcome": "Welkom", "dash": "Dashboard", "prop": "CV-Propulsie", "match": "Interviews", "off": "Jobs & Dispatch", "acc": "Account"},
    "Русский": {"label": "Профиль & ATS", "welcome": "Добро пожаловать", "dash": "Панель", "prop": "Продвижение CV", "match": "Интервью", "off": "Вакансии", "acc": "Аккаунт"},
    "中文": {"label": "个人资料 & ATS", "welcome": "欢迎", "dash": "仪表板", "prop": "简历推广", "match": "面试", "off": "职位与分发", "acc": "账户"},
    "日本語": {"label": "プロフィール & ATS", "welcome": "ようこそ", "dash": "ダッシュボード", "prop": "CV推進", "match": "面接", "off": "求人と配信", "acc": "アカウント"},
    "한국어": {"label": "프로필 & ATS", "welcome": "환영합니다", "dash": "대시보드", "prop": "CV 추진", "match": "면접", "off": "채용 및 발송", "acc": "계정"},
    "العربية": {"label": "الملف الشخصي & ATS", "welcome": "أهلاً بك", "dash": "لوحة التحكم", "prop": "دفع السيرة الذاتية", "match": "مقابلات", "off": "وظائف", "acc": "الحساب"},
    "Türkçe": {"label": "Profil & ATS", "welcome": "Hoş geldiniz", "dash": "Panel", "prop": "CV İtici Gücü", "match": "Mülakatlar", "off": "İşler & Dağıtım", "acc": "Hesap"},
    "Polski": {"label": "Profil & ATS", "welcome": "Witamy", "dash": "Pulpit", "prop": "Propulsja CV", "match": "Rozmowy", "off": "Oferty & Wysyłka", "acc": "Konto"},
    "Svenska": {"label": "Profil & ATS", "welcome": "Välkommen", "dash": "Panel", "prop": "CV-propulsion", "match": "Intervjuer", "off": "Jobb & Utskick", "acc": "Konto"},
    "Norsk": {"label": "Profil & ATS", "welcome": "Velkommen", "dash": "Dashbord", "prop": "CV-fremdrift", "match": "Intervjuer", "off": "Jobber & Utsendelse", "acc": "Konto"},
    "Dansk": {"label": "Profil & ATS", "welcome": "Velkommen", "dash": "Instrumentbræt", "prop": "CV-fremdrift", "match": "Interviews", "off": "Job & Afsendelse", "acc": "Konto"},
    "Suomi": {"label": "Profiili & ATS", "welcome": "Tervetuloa", "dash": "Kojelauta", "prop": "CV-propulsio", "match": "Haastattelut", "off": "Työt & Lähetys", "acc": "Tili"},
    "Ελληνικά": {"label": "Προφίλ & ATS", "welcome": "Καλώς ήρθατε", "dash": "Πίνακας ελέγχου", "prop": "Προώθηση CV", "match": "Συνεντεύξεις", "off": "Θέσεις εργασίας", "acc": "Λογαριασμός"},
    "Tiếng Việt": {"label": "Hồ sơ & ATS", "welcome": "Chào mừng", "dash": "Bảng điều khiển", "prop": "Thúc đẩy CV", "match": "Phỏng vấn", "off": "Việc làm", "acc": "Tài khoản"}
}

# --- SÉLECTEUR LANGUE (Haut) ---
col_lang, _ = st.columns([1, 10])
with col_lang:
    if "lang" not in st.session_state: st.session_state.lang = "Français"
    st.session_state.lang = st.selectbox("🌐", list(LANGUAGES.keys()))
t = LANGUAGES[st.session_state.lang]

# --- INIT SUPABASE ---
try:
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
except:
    st.error("Erreur connexion base.")

# --- NAVIGATION ---
if "auth" not in st.session_state: st.session_state.update({"auth": False, "premium": False})

if not st.session_state.auth:
    st.title("zipngo 👍")
    st.markdown(f"### {t['welcome']} ! Plateforme RH intelligente.")
    role = st.radio("Accès :", ["Candidat", "Employeur"], horizontal=True)
    if st.button("Connexion"): st.session_state.update({"auth": True, "user_type": role}); st.rerun()
else:
    with st.sidebar:
        if st.session_state.get("premium"): st.success("✨ Premium Actif")
        else: st.warning("⚠️ Compte Standard")
        menu = st.radio("Navigation", [t["dash"], t["label"], t["prop"], t["match"], t["off"], t["acc"]])
        if st.button("🚪 Déconnexion"): st.session_state.auth = False; st.rerun()

    # --- VUES ET MODES D'EMPLOI ---
    if menu == t["dash"]:
        st.header(t["dash"])
        st.info(f"💡 **Mode d'emploi {st.session_state.user_type} :** Utilisez la barre latérale pour naviguer. Le Premium débloque vos accès illimités.")
    
    elif menu == t["label"]:
        st.header(t["label"])
        st.file_uploader("Charger CV")
        if st.button("IA Score ATS"): st.write("Score : 85%")

    elif menu == t["prop"]:
        st.header(t["prop"])
        if st.button("Récupérer 20 cibles"):
            st.link_button("Candidater (Envoi BCC)", "mailto:?bcc=cibles@email.fr&subject=Candidature")
            st.warning("Ajoutez votre CV en PJ !")

    elif menu == t["match"]:
        st.header(t["match"])
        st.link_button("Rejoindre entretien (Jitsi)", "https://meet.jit.si/zipngo")

    elif menu == t["off"]:
        st.header(t["off"])
        if st.button("🚀 Diffuser en 1 clic"): st.balloons()

    elif menu == t["acc"]:
        st.header(t["acc"])
        if st.session_state.user_email == "creationsites06@gmail.com":
            st.download_button("📥 Export CSV", "data", "zipngo_export.csv")

st.markdown("---")
st.markdown("© 2026 zipngo | Liliane RAKOTOBE")
