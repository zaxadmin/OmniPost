import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin-bottom: 0px; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }
    .feature-card { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 1px solid #e1f5fe; box-shadow: 0 10px 20px rgba(0, 33, 71, 0.05); height: 100%; text-align: center; }
    .price-tag { background-color: #002147; color: #00E5FF; padding: 10px 20px; border-radius: 20px; font-weight: bold; display: inline-block; margin: 15px 0; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: scale(1.01); }
    .footer-text { font-size: 11px; color: #888888; text-align: center; padding: 10px; font-family: sans-serif; }
    .footer-icon { color: #F3812B; font-size: 18px; vertical-align: middle; margin-left: 5px; text-decoration: none; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DICTIONNAIRE COMPLET (20 LANGUES) ---
LANGS = {
    "Français 🇫🇷": {"cand": "Essai 1 jour : 1 relooking IA et 1 test ATS.", "emp": "Essai 7 jours : Accès talents et visio."},
    "English 🇺🇸": {"cand": "1-day trial: 1 AI makeover and 1 ATS test.", "emp": "7-day trial: Talent access and video."},
    "Malagasy 🇲🇬": {"cand": "Andrana 1 andro: Fanavaozana 1 sy fizahana ATS 1.", "emp": "Andrana 7 andro: Tahiry sy horonantsary."},
    "Español 🇪🇸": {"cand": "Prueba de 1 día: 1 rediseño IA y 1 test ATS.", "emp": "Prueba de 7 días: Acceso y video."},
    "Deutsch 🇩🇪": {"cand": "1-Tag-Test: 1 KI-Makeover.", "emp": "7-Tage-Test: Talentzugang."},
    "Italiano 🇮🇹": {"cand": "Prova 1 giorno: 1 restyling IA.", "emp": "Prova 7 giorni: Accesso."},
    "Português 🇧🇷": {"cand": "Teste 1 dia: 1 reestilização IA.", "emp": "Teste 7 dias: Acesso."},
    "Русский 🇷🇺": {"cand": "1 день: 1 ИИ-преображение.", "emp": "7 дней: Доступ."},
    "日本語 🇯🇵": {"cand": "1日試用：AIリメイク1回。", "emp": "7日間試用：タレントアクセス。"},
    "العربية 🇸🇦": {"cand": "تجربة يوم: تحسين واحد.", "emp": "تجربة 7 أيام: وصول كامل."},
    "Türkçe 🇹🇷": {"cand": "1 günlük deneme.", "emp": "7 günlük deneme."},
    "Nederlands 🇳🇱": {"cand": "1 dag proef.", "emp": "7 dagen proef."},
    "한국어 🇰🇷": {"cand": "1일 체험.", "emp": "7일 체험."},
    "中文 🇨🇳": {"cand": "1天试用。", "emp": "7天试用。"},
    "हिन्दी 🇮🇳": {"cand": "1 दिन का परीक्षण.", "emp": "7 दिन का परीक्षण."},
    "Polski 🇵🇱": {"cand": "1 dzień próbny.", "emp": "7 dni próbnych."},
    "Svenska 🇸🇪": {"cand": "1 dags prov.", "emp": "7 dagars prov."},
    "Tiếng Việt 🇻🇳": {"cand": "Dùng thử 1 ngày.", "emp": "Dùng thử 7 ngày."},
    "Bahasa Indonesia 🇮🇩": {"cand": "Uji coba 1 hari.", "emp": "Uji coba 7 hari."},
    "ไทย 🇹🇭": {"cand": "ทดลองใช้ 1 วัน.", "emp": "ทดลองใช้ 7 วัน."}
}

# --- 3. CONNEXIONS SUPABASE ---
try:
    supabase = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
except:
    st.error("Erreur de secrets Supabase.")

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. INTERFACE ACCUEIL ---
if not st.session_state.user:
    c_lang, _ = st.columns([1, 2])
    with c_lang:
        sel_lang = st.selectbox("🌐 Language", list(LANGS.keys()))
    
    st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="feature-card"><h2 style="color:#002147;">Candidat</h2><p>{LANGS[sel_lang]["cand"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="feature-card"><h2 style="color:#002147;">Employeur</h2><p>{LANGS[sel_lang]["emp"]}</p></div>', unsafe_allow_html=True)

    t_log, t_reg = st.tabs(["🔑 Connexion", "📝 Inscription"])
    with t_reg:
        re = st.text_input("Email", key="reg_e")
        rp = st.text_input("Pass", type="password", key="reg_p")
        rr = st.radio("Je suis :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("Démarrer l'essai 👍"):
            days = 1 if rr == "Candidat" else 7
            exp = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            supabase.table("users").insert({"email": re, "password": rp, "role": rr, "expire_at": exp, "status": "essai", "tokens_ia": 1, "lang_pref": sel_lang}).execute()
            st.success("Compte créé !")

    with t_log:
        le = st.text_input("Email", key="log_e")
        lp = st.text_input("Pass", type="password", key="log_p")
        if st.button("Se connecter 👍"):
            res = supabase.table("users").select("*").eq("email", le).eq("password", lp).execute()
            if res.data:
                u = res.data[0]
                st.session_state.user = le
                st.session_state.role = u['role']
                st.session_state.expire_at = u['expire_at']
                st.session_state.status = u['status']
                st.rerun()

# --- 5. ESPACE MEMBRE ---
else:
    with st.sidebar:
        st.markdown('<p style="font-size:30px; font-weight:900; color:#002147;">zaxx</p>', unsafe_allow_html=True)
        st.write(f"👤 {st.session_state.user}")
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    if st.session_state.role == "Candidat":
        st.subheader("Espace Candidat")
        if st.button("Activer 3 mois (3€) 👍"):
            new_exp = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
            supabase.table("users").update({"expire_at": new_exp, "status": "premium"}).eq("email", st.session_state.user).execute()
            st.success("Compte activé !")
    else:
        st.subheader("Espace Recruteur")

# --- 6. FOOTER ---
st.divider()
f1, f2, f3 = st.columns(3)
with f1:
    with st.expander("⚖️ Mentions"):
        st.write("Éditeur : RAKOTOBE Liliane.")
with f2:
    with st.expander("📜 CGV"):
        st.write("Produit numérique. Pas de remboursement.")
with f3:
    st.markdown(f'<div class="footer-text">© 2026 <b>RAKOTOBE Liliane</b> | <a href="mailto:creationsites06@gmail.com" class="footer-icon"><i class="fa-regular fa-envelope"></i></a></div>', unsafe_allow_html=True)
