import streamlit as st
from supabase import create_client
from ai_engine import coach_ia, generate_offer
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# Injection CSS, FontAwesome et Design
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    /* Typographie et Couleurs */
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin-bottom: 0px; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Cartes et Éléments UI */
    .feature-card { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 1px solid #e1f5fe; box-shadow: 0 10px 20px rgba(0, 33, 71, 0.05); height: 100%; text-align: center; }
    .price-tag { background-color: #002147; color: #00E5FF; padding: 10px 20px; border-radius: 20px; font-weight: bold; display: inline-block; margin: 15px 0; }
    .fake-payment { background-color: #f0f7ff; border: 2px dashed #002147; padding: 20px; border-radius: 10px; margin: 20px 0; }
    
    /* Boutons */
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: scale(1.01); }

    /* Footer */
    .footer-text { font-size: 11px; color: #888888; text-align: center; padding: 10px; }
    .footer-icon { color: #F3812B; font-size: 18px; vertical-align: middle; margin-left: 5px; transition: 0.3s; }
    .footer-icon:hover { transform: scale(1.2); color: #002147; }
    .stExpander { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. DICTIONNAIRE DES 20 LANGUES ---
LANGS = {
    "Français 🇫🇷": {"cand": "Essai 1 jour : 1 relooking IA et 1 test ATS.", "emp": "Essai 7 jours : Accès talents et visio."},
    "English 🇺🇸": {"cand": "1-day trial: 1 AI makeover and 1 ATS test.", "emp": "7-day trial: Talent access and video."},
    "Malagasy 🇲🇬": {"cand": "Andrana 1 andro: Fanavaozana 1 sy fizahana ATS 1.", "emp": "Andrana 7 andro: Tahiry sy horonantsary."},
    "Español 🇪🇸": {"cand": "Prueba de 1 día: 1 rediseño IA y 1 test ATS.", "emp": "Prueba de 7 días: Acceso y video."},
    "Deutsch 🇩🇪": {"cand": "1-Tag-Test: 1 KI-Makeover und 1 ATS-Test.", "emp": "7-Tage-Test: Talentzugang und Video."},
    "Italiano 🇮🇹": {"cand": "Prova di 1 giorno: 1 restyling IA e 1 test ATS.", "emp": "Prova di 7 giorni: Accesso e video."},
    "Português 🇧🇷": {"cand": "Teste de 1 dia: 1 reestilização IA e 1 teste ATS.", "emp": "Teste de 7 dias: Acesso e vídeo."},
    "Русский 🇷🇺": {"cand": "1 день: 1 ИИ-преображение и 1 ATS-тест.", "emp": "7 дней: Доступ и видео."},
    "日本語 🇯🇵": {"cand": "1日試用：AIリメイク1回とATSテスト1回。", "emp": "7日間試用：タレントアクセスとビデオ。"},
    "العربية 🇸🇦": {"cand": "تجربة يوم: تحسين واحد واختبار ATS واحد.", "emp": "تجربة 7 أيام: وصول كامل وفيديو."},
    "Türkçe 🇹🇷": {"cand": "1 günlük deneme: 1 yapay zeka yenileme ve 1 ATS testi.", "emp": "7 günlük deneme: Yetenek erişimi ve video."},
    "Nederlands 🇳🇱": {"cand": "1 dag proef: 1 AI-make-over en 1 ATS-test.", "emp": "7 dagen proef: Toegang en video."},
    "한국어 🇰🇷": {"cand": "1일 체험: AI 메이크오버 1회 및 ATS 테스트 1회.", "emp": "7일 체험: 인재 액세스 및 비디오."},
    "中文 🇨🇳": {"cand": "1天试用：1次AI修改和1次ATS测试。", "emp": "7天试用：人才访问和视频。"},
    "हिन्दी 🇮🇳": {"cand": "1 दिन का परीक्षण: 1 एआई मेकओवर और 1 एटीएस टेस्ट।", "emp": "7 दिन का परीक्षण: पहुंच और वीडियो।"},
    "Polski 🇵🇱": {"cand": "1 dzień próbny: 1 metamorfoza AI i 1 test ATS.", "emp": "7 dni próbnych: Dostęp i wideo."},
    "Svenska 🇸🇪": {"cand": "1 dags prov: 1 AI-makeover och 1 ATS-test.", "emp": "7 dagars prov: Tillgång och video."},
    "Tiếng Việt 🇻🇳": {"cand": "Dùng thử 1 ngày: 1 lần sửa hồ sơ và 1 bài test ATS.", "emp": "Dùng thử 7 ngày: Truy cập và video."},
    "Bahasa Indonesia 🇮🇩": {"cand": "Uji coba 1 hari: 1 desain ulang AI dan 1 tes ATS.", "emp": "Uji coba 7 hari: Akses dan video."},
    "ไทย 🇹🇭": {"cand": "ทดลองใช้ 1 วัน: ปรับแต่ง AI 1 ครั้งและทดสอบ ATS 1 ครั้ง", "emp": "ทดลองใช้ 7 วัน: เข้าถึงข้อมูลและวิดีโอ"}
}

# --- 3. CONNEXIONS SUPABASE ---
try:
    supabase_auth = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
    supabase_data = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])
except Exception:
    st.error("Erreur de connexion aux secrets Supabase.")

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. ACCUEIL (NON CONNECTÉ) ---
if not st.session_state.user:
    # Sélecteur de langue en haut à gauche
    c_lang, _ = st.columns([1, 3])
    with c_lang:
        sel_lang = st.selectbox("🌐 Language / Langue", list(LANGS.keys()))
    
    st.markdown("<h1 style='text-align: center; margin-bottom: 0; color: #F3812B; font-size: 80px;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="feature-card"><h2 style="color:#002147;">Candidat</h2><p>{LANGS[sel_lang]["cand"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="feature-card"><h2 style="color:#002147;">Employeur</h2><p>{LANGS[sel_lang]["emp"]}</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    t_log, t_reg = st.tabs(["🔑 Connexion", "📝 Inscription (Essai gratuit)"])
    
    with t_reg:
        re, rp = st.text_input("Email", key="re"), st.text_input("Mot de passe", type="password", key="rp")
        rr = st.radio("Je suis un :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("Démarrer mon essai gratuit 👍"):
            days = 1 if rr == "Candidat" else 7
            exp = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            supabase_auth.table("users").insert({
                "email": re, "password": rp, "role": rr, "expire_at": exp, "status": "essai", "tokens_ia": 1, "lang_pref": sel_lang
            }).execute()
            st.success(f"Compte créé ! Votre essai expire le {exp}.")

    with t_log:
        le, lp = st.text_input("Email", key="le"), st.text_input("Mot de passe", type="password", key="lp")
        if st.button("Entrer dans Zaxx 👍"):
            res = supabase_auth.table("users").select("*").eq("email", le).eq("password", lp).execute()
            if res.data:
                u = res.data[0]
                st.session_state.user = le
                st.session_state.role = u['role']
                st.session_state.expire_at = u['expire_at']
                st.session_state.status = u['status']
                st.session_state.tokens = u.get('tokens_ia', 0)
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

# --- 5. ESPACE CONNECTÉ ---
else:
    is_expired = datetime.strptime(st.session_state.expire_at, '%Y-%m-%d') < datetime.now()

    with st.sidebar:
        st.markdown('<p style="font-size:30px; font-weight:900; color:#002147;">zaxx</p>', unsafe_allow_html=True)
        st.write(f"👤 {st.session_state.user}")
        if is_expired: st.error("⌛ Accès expiré")
        else: st.info(f"⏳ Fin d'accès : {st.session_state.expire_at}")
        
        sel_lang = st.selectbox("🌐 Langue de l'IA", list(LANGS.keys()))
        
        st.divider()
        if st.button("❌ Supprimer mon compte"):
            if st.checkbox("Confirmer la suppression irréversible"):
                supabase_auth.table("users").delete().eq("email", st.session_state.user).execute()
                st.session_state.user = None
                st.rerun()
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    # --- INTERFACE CANDIDAT ---
    if st.session_state.role == "Candidat":
        t1, t2, t3 = st.tabs(["🎥 Mes Entretiens", "🪄 Services IA", "💳 Activer 3 mois"])
        
        with t2:
            if is_expired and st.session_state.status == "essai":
                st.warning("Essai terminé. Activez l'accès 3 mois pour continuer.")
            else:
                st.subheader(f"Relooking & ATS ({sel_lang})")
                st.write(f"Crédits restants : {st.session_state.tokens}")
                cv_file = st.file_uploader("Uploader CV ou Lettre de motivation")
                if st.button("Lancer l'Analyse 👍") and st.session_state.tokens > 0:
                    st.write("Analyse IA en cours...")
                    if st.session_state.status == "essai":
                        supabase_auth.table("users").update({"tokens_ia": 0}).eq("email", st.session_state.user).execute()
                        st.session_state.tokens = 0

        with t1:
            st.link_button("🎥 Ma Salle de Visio", f"https://meet.jit.si/Zaxx-User-{st.session_state.user.split('@')[0]}")

        with t3:
            st.subheader("Paiement Unique (90 jours)")
            st.markdown('<div class="price-tag">Tarif : 3€</div>', unsafe_allow_html=True)
            st.markdown('<div class="fake-payment">💳 <b>Paiement Virtuel</b><br>Accès immédiat. Aucun abonnement caché.</div>', unsafe_allow_html=True)
            if st.button("Activer mes 3 mois 👍"):
                new_exp = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                supabase_auth.table("users").update({"expire_at": new_exp, "status": "premium", "tokens_ia": 999}).eq("email", st.session_state.user).execute()
                st.session_state.expire_at, st.session_state.status = new_exp, "premium"
                st.rerun()

    # --- INTERFACE EMPLOYEUR ---
    else:
        t1, t2, t3 = st.tabs(["🔍 Rechercher", "📅 Planning", "💳 Activer 3 mois"])
        
        with t1:
            if is_expired and st.session_state.status == "essai":
                st.warning("Essai entreprise terminé. Souscrivez pour voir les talents.")
            else:
                st.info("Moteur de recherche de talents actif.")

        with t3:
            st.subheader("Accès Recruteur (90 jours)")
            st.markdown('<div class="price-tag">Tarif : 49€</div>', unsafe_allow_html=True)
            if st.button("Activer l'accès Entreprise 👍"):
                new_exp = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                supabase_auth.table("users").update({"expire_at": new_exp, "status": "premium"}).eq("email", st.session_state.user).execute()
                st.session_state.expire_at, st.session_state.status = new_exp, "premium"
                st.rerun()

# --- 6. FOOTER JURIDIQUE & CONTACT ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    with st.expander("⚖️ Mentions Légales & Copyright"):
        st.write("""
        **Propriété :** L'application Zipngo-Zaxx est la propriété exclusive de **RAKOTOBE Liliane**.  
        Toute reproduction du design ou du concept est interdite.  
        **Hébergement :** Streamlit Cloud.
        """)

with f_col2:
    with st.expander("📜 CGV (Paiement & Remboursement)"):
        st.write("""
        **Nature :** Produit numérique virtuel à exécution immédiate.  
        **Remboursement :** Aucun remboursement possible après accès au service (Art. L221-28).  
        **Engagement :** Pas d'abonnement. Paiement unique pour 3 mois.
        """)

with f_col3:
    st.markdown(f"""
        <div class="footer-text">
            © 2026 Copyright par <b>RAKOTOBE Liliane</b> | 
            <a href="mailto:creationsites06@gmail.com" title="Envoyer un email">
                <i class="fa-regular fa-envelope footer-icon"></i>
            </a>
        </div>
    """, unsafe_allow_html=True)
