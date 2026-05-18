import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="neocrm.zaxx | Platform Global Ecosystem", layout="wide")

# --- SYSTÈME DE LANGUES TRADUITES (20 LANGUES COMPLETES) ---
LANG_MAP = {
    "Français": "fr", "English (US)": "en", "Malgache": "mg", "Español": "es", 
    "Deutsch": "de", "Italiano": "it", "Português": "pt", "Nederlands": "nl",
    "Русский": "ru", "日本語": "ja", "한국어": "ko", "中文": "zh",
    "العربية": "ar", "हिन्दी": "hi", "Türkçe": "tr", "Polski": "pl",
    "Svenska": "sv", "Tiếng Việt": "vi", "ไทย": "th", "Ελληνικά": "el"
}

TEXTS = {
    "Français": {
        "intro": "L'écosystème CRM de pointe pour propulser vos ventes.",
        "desc": "neocrm.zaxx est la solution que nous avons conçue pour centraliser l'intelligence commerciale, optimiser vos conversions et collaborer en temps réel.",
        "uid": "Identifiant de connexion / Numéro de Pass", "pwd": "Mot de passe",
        "btn_login": "ACCÉDER À MON CRM / ACTIVATION", "btn_lost": "mots de passe perdu", "btn_create": "CREER UN COMPTE"
    },
    "English (US)": {
        "intro": "The cutting-edge CRM ecosystem to boost your sales.",
        "desc": "neocrm.zaxx is the solution we designed to centralize commercial intelligence, optimize conversions, and collaborate in real-time.",
        "uid": "Login ID / Pass Number", "pwd": "Password",
        "btn_login": "ACCESS MY CRM / ACTIVATION", "btn_lost": "lost password", "btn_create": "CREATE AN ACCOUNT"
    },
    "Malgache": {
        "intro": "Ny rafitra CRM farany indrindra hampitomboana ny fivarotanao.",
        "desc": "neocrm.zaxx dia vahaolana namboarinay hanambarana ny fahaiza-manao ara-barotra sy hiaraha-miasa amin'ny fotoana tena izy.",
        "uid": "Anarana fidirana / Laharan'ny Pass", "pwd": "Teny miafina",
        "btn_login": "HIDITRA AMIN'NY CRM / ACTIVATION", "btn_lost": "hadino ny teny miafina", "btn_create": "HANOKATRA KAONTY"
    },
    "Español": {
        "intro": "El ecosistema CRM de vanguardia para impulsar sus ventas.",
        "desc": "neocrm.zaxx es la solution diseñada para centralizar la inteligencia comercial, optimizar conversiones y colaborar en tiempo real.",
        "uid": "Identificación de ingreso / Número de Pase", "pwd": "Contraseña",
        "btn_login": "ACCEDER A MI CRM / ACTIVACIÓN", "btn_lost": "contraseña perdida", "btn_create": "CREAR UNA CUENTA"
    },
    "Deutsch": {
        "intro": "Das führende CRM-Ökosystem zur Steigerung Ihres Umsatzes.",
        "desc": "neocrm.zaxx ist die Lösung, die wir entwickelt haben, um Vertriebsintelligenz zu zentralisieren, Conversions zu optimieren und in Echtzeit zusammenzuarbeiten.",
        "uid": "Anmelde-ID / Passnummer", "pwd": "Passwort",
        "btn_login": "AUF MEIN CRM ZUGREIFEN / AKTIVIERUNG", "btn_lost": "Passwort vergessen", "btn_create": "KONTO ERSTELLEN"
    },
    "Italiano": {
        "intro": "L'ecosistema CRM all'avanguardia per incrementare le tue vendite.",
        "desc": "neocrm.zaxx è la soluzione progettata per centralizzare l'intelligence commerciale, ottimizzare le conversioni e collaborare in tempo reale.",
        "uid": "ID di accesso / Numero di Pass", "pwd": "Password",
        "btn_login": "ACCEDI AL MIO CRM / ATTIVAZIONE", "btn_lost": "password smarrita", "btn_create": "CREA UN ACCOUNT"
    },
    "Português": {
        "intro": "O ecossistema CRM de ponta para impulsionar suas vendas.",
        "desc": "neocrm.zaxx é a solução que concebemos para centralizar a inteligência comercial, otimizar conversões e colaborar em tempo real.",
        "uid": "ID de login / Número do Passe", "pwd": "Senha",
        "btn_login": "ACESSAR MEU CRM / ATIVAÇÃO", "btn_lost": "senha perdida", "btn_create": "CRIAR UMA CONTA"
    },
    "Nederlands": {
        "intro": "Het geavanceerde CRM-ecosysteem om uw verkoop te stimuleren.",
        "desc": "neocrm.zaxx is de oplossing die we hebben ontworpen om commerciële intelligentie te centraliseren, conversies te optimaliseren en in realtime samen te werken.",
        "uid": "Inlog-ID / Pasnummer", "pwd": "Wachtwoord",
        "btn_login": "TOEGANG TOT MIJN CRM / ACTIVATIE", "btn_lost": "wachtwoord vergeten", "btn_create": "ACCOUNT AANMAKEN"
    },
    "Русский": {
        "intro": "Передовая экосистема CRM для стимулирования ваших продаж.",
        "desc": "neocrm.zaxx — это решение, разработанное нами для централизации коммерческой аналитики, оптимизации конверсий и совместной работы в реальном времени.",
        "uid": "Идентификатор входа / Номер пропуска", "pwd": "Пароль",
        "btn_login": "ВОЙТИ В МОЙ CRM / АКТИВАЦИЯ", "btn_lost": "забыли пароль", "btn_create": "СОЗДАТЬ АККАУНТ"
    },
    "日本語": {
        "intro": "売上を伸ばすための最先端のCRMエコシステム。",
        "desc": "neocrm.zaxxは、営業インテリジェンスの集中化、コンバージョンの最適化、リアルタイムのコラボレーションのために設計されたソリューションです。",
        "uid": "ログインID / パス番号", "pwd": "パスワード",
        "btn_login": "CRMにアクセス / アクティベーション", "btn_lost": "パスワードを忘れた場合", "btn_create": "アカウント作成"
    },
    "한국어": {
        "intro": "매출 증대를 위한 최첨단 CRM 에코시스템.",
        "desc": "neocrm.zaxx는 영업 인텔리전스를 중앙화하고 전환을 최적化하며 실시간으로 협업할 수 있도록 설계된 솔루션입니다.",
        "uid": "로그인 ID / 패스 번호", "pwd": "비밀번호",
        "btn_login": "내 CRM 액세스 / 활성화", "btn_lost": "비밀번호를 잊으셨나요", "btn_create": "계정 만들기"
    },
    "中文": {
        "intro": "助力销售增长的尖端 CRM 生态系统。",
        "desc": "neocrm.zaxx 是我们专为集中商业智能、优化转化和实时协作而设计的解决方案。",
        "uid": "登录 ID / 通行证号", "pwd": "密码",
        "btn_login": "访问 my CRM / 激活", "btn_lost": "忘记密码", "btn_create": "创建账户"
    },
    "العربية": {
        "intro": "نظام CRM المتطور لتعزيز مبيعاتك.",
        "desc": "neocrm.zaxx هو الحل الذي صممناه لمركزية الذكاء التجاري، وتحسين التحويلات، والتعاون في الوقت الفعلي.",
        "uid": "معرف تسجيل الدخول / رقم الممر", "pwd": "كلمة المرور",
        "btn_login": "الوصول إلى CRM الخاص بي / التفعيل", "btn_lost": "فقدت كلمة المرور", "btn_create": "إنشاء حساب"
    },
    "हिन्दी": {
        "intro": "आपकी बिक्री बढ़ाने के लिए अत्याधुनिक CRM पारिस्थितिकी तंत्र।",
        "desc": "neocrm.zaxx वाणिज्यिक खुफिया जानकारी को केंद्रीकृत करने, रूपांतरणों को अनुकूलित करने gas और वास्तविक समय में सहयोग करने के लिए हमारे द्वारा डिज़ाइन किया गया समाधान है।",
        "uid": "लॉगिन आईडी / पास नंबर", "pwd": "पासवर्ड",
        "btn_login": "मेरे CRM तक पहुँचें / सक्रियण", "btn_lost": "पासवर्ड भूल गए", "btn_create": "खाता बनाएं"
    },
    "Türkçe": {
        "intro": "Satışlarınızı artırmak için en son teknoloji CRM ekosistemi.",
        "desc": "neocrm.zaxx, ticari zekayı merkezileştirmek, dönüşümleri optimize etmek ve gerçek zamanlı iş birliği yapmak için tasarladığımız çözümdür.",
        "uid": "Kullanıcı Adı / Geçiş Numarası", "pwd": "Şifre",
        "btn_login": "CRM'İME ERİŞ / AKTİVASYON", "btn_lost": "şifremi unuttum", "btn_create": "HESAP OLUŞTUR"
    },
    "Polski": {
        "intro": "Nowoczesny ekosystem CRM, który napędzi Twoją sprzedaż.",
        "desc": "neocrm.zaxx to rozwiązanie zaprojektowane w celu centralizacji danych handlowych, optymalizacji konwersji i współpracy w czasie rzeczywistym.",
        "uid": "Identyfikator logowania / Numer karnetu", "pwd": "Hasło",
        "btn_login": "DOSTĘP DO MOJEGO CRM / AKTYWACJA", "btn_lost": "zapomniane hasło", "btn_create": "ZAŁÓŻ KONTO"
    },
    "Svenska": {
        "intro": "Det banbrytande CRM-ekosystemet för att öka din försäljning.",
        "desc": "neocrm.zaxx är lösningen vi designat för att centralisera affärsintelligens, optimera konverteringar och samarbeta i realtid.",
        "uid": "Inloggnings-ID / Passnummer", "pwd": "Lösenord",
        "btn_login": "TILLGÅNG TILL MITT CRM / AKTIVERING", "btn_lost": "glömt lösenord", "btn_create": "SKAPA KONTO"
    },
    "Tiếng Việt": {
        "intro": "Hệ sinh thái CRM tiên tiến để thúc đẩy doanh số bán hàng của bạn.",
        "desc": "neocrm.zaxx là giải pháp chúng tôi thiết kế để tập trung trí tuệ thương mại, tối ưu hóa chuyển đổi và cộng tác trong thời gian thực.",
        "uid": "ID Đăng nhập / Số thẻ", "pwd": "Mật khẩu",
        "btn_login": "TRUY CẬP CRM CỦA TÔI / KÍCH HOẠT", "btn_lost": "quên mật khẩu", "btn_create": "TẠO TÀI KHOẢN"
    },
    "ไทย": {
        "intro": "ระบบนิเวศ CRM ที่ล้ำสมัยเพื่อเพิ่มยอดขายของคุณ",
        "desc": "neocrm.zaxx คือโซลูชันที่เราออกแบบมาเพื่อรวมศูนย์ข้อมูลเชิงลึกทางการค้า เพิ่มประสิทธิภาพการแปลง และทำงานร่วมกันแบบเรียลไทม์",
        "uid": "รหัสเข้าสู่ระบบ / หมายเลขบัตร", "pwd": "รหัสผ่าน",
        "btn_login": "เข้าสู่ระบบ CRM / เปิดใช้งาน", "btn_lost": "ลืมรหัสผ่าน", "btn_create": "สร้างบัญชี"
    },
    "Ελληνικά": {
        "intro": "Το κορυφαίο οικοσύστημα CRM για την ενίσχυση των πωλήσεών σας.",
        "desc": "Το neocrm.zaxx είναι η λύση που σχεδιάσαμε για τη συγκέντρωση της εμπορικής ευφυΐας, τη βελτιστοποίηση των μετατροπών και τη συνεργασία σε πραγματικό χρόνο.",
        "uid": "ID Σύνδεσης / Αριθμός Πάσου", "pwd": "Κωδικός πρόσβασης",
        "btn_login": "ΠΡΟΣΒΑΣΗ ΣΤΟ CRM ΜΟΥ / ΕΝΕΡΓΟΠΟΙΗΣΗ", "btn_lost": "ξεχάσατε τον κωδικό", "btn_create": "ΔΗΜΙΟΥΡΓΙΑ ΛΟΓΑΡΙΑΣ"
    }
}

LANG_COMMANDO = ["Français", "English (US)", "Malgache", "Español", "Deutsch"]
LANG_SUPER_MANAGER = ["English (US)", "Français"]
LANG_PUBLIC_ET_CLIENT = list(LANG_MAP.keys()) 

# --- INITIALISATION DE LA BASE SESSIONS ---
if "pass_database" not in st.session_state:
    st.session_state.pass_database = {
        "candidat_test": {"pwd": "candidat2026", "type": "Candidat", "role": "Client", "activation": datetime.now(), "duree_jours": 1},
        "employeur_test": {"pwd": "employeur2026", "type": "Employeur", "role": "Client", "activation": datetime.now(), "duree_jours": 7},
        "admin_test": {"pwd": "Zaxx2026!", "type": "SuperUser", "role": "SuperManager", "activation": datetime.now(), "duree_jours": 9999}
    }

if "interview_session" not in st.session_state:
    st.session_state.interview_session = {"planned": False, "date": None, "time": None, "status": "Aucun entretien planifié", "room_url": "https://meet.jit.si/ZaxxIntelligenceInterviewRoom"}

if "ats_score" not in st.session_state: st.session_state.ats_score = None
if "ats_retested" not in st.session_state: st.session_state.ats_retested = False

# --- SYSTEME STYLES NEO & PREMIUM BLOCKS ---
def apply_neo_theme():
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC; color: #1A237E; }
        [data-testid="stSidebar"] { background-color: #1A237E !important; border-right: 3px solid #00E5FF; }
        [data-testid="stSidebar"] * { color: #FFFFFF !important; }
        .stButton>button { background: #1A237E !important; color: #FFFFFF !important; font-weight: 700; border-radius: 8px; width: 100%; height: 45px; }
        div[data-testid='column'] > div > div:nth-child(9) button { background-color: #00E5FF !important; color: #1A237E !important; border: none !important; }
        .pass-box { padding: 20px; background-color: #E0F7FA; border-left: 5px solid #00E5FF; border-radius: 6px; margin-bottom: 20px;}
        .premium-box { padding: 25px; background: linear-gradient(135deg, #1A237E 0%, #0D1B60 100%); color: white !important; border-radius: 12px; border: 2px solid #00E5FF; text-align: center; margin-top: 20px; }
        .premium-box h3 { color: #00E5FF !important; margin-top:0; }
        .premium-btn { display: inline-block; background-color: #00E5FF; color: #1A237E !important; font-weight: bold; padding: 12px 30px; border-radius: 25px; text-decoration: none; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,229,255,0.4); }
        .ai-box { padding: 20px; background-color: #F0F4F8; border-radius: 8px; border-left: 5px solid #1A237E; margin: 15px 0; }
        .cv-template { padding: 15px; border: 1px dashed #1A237E; border-radius: 6px; background: #FFF; text-align: center; margin-bottom: 10px; }
        .footer { text-align: center; padding: 25px; border-top: 1px solid #E2E8F0; margin-top: 50px; }
        .legal-link { color: #64748b; text-decoration: none; font-size: 11px; margin: 0 15px; }
    </style>
    """, unsafe_allow_html=True)

if "auth" not in st.session_state: st.session_state.auth = False
if "user_role" not in st.session_state: st.session_state.user_role = None
if "user_type" not in st.session_state: st.session_state.user_type = None
if "view" not in st.session_state: st.session_state.view = "login"

apply_neo_theme()

# --- ACCÈS DE CONNEXION ---
if not st.session_state.auth:
    if st.session_state.view == "login":
        _, col, _ = st.columns([1, 1.4, 1])
        with col:
            selected_lang = st.selectbox("🌐", LANG_PUBLIC_ET_CLIENT, label_visibility="collapsed", key="login_lang")
            t = TEXTS.get(selected_lang, TEXTS["English (US)"])
            st.markdown(f"<h1 style='text-align:center; font-size: 52px; margin-bottom:0;'><span style='color:#1A237E;'>neocrm</span><span style='color:#00E5FF;'>.zaxx</span></h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1A237E; font-size:18px;'>{t['intro']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#64748b; font-size:14px; line-height:1.3;'>{t['desc']}</p>", unsafe_allow_html=True)
            st.divider()
            uid = st.text_input(t['uid'])
            pwd = st.text_input(t['pwd'], type="password")
            
            if st.button(t['btn_login']):
                if uid in st.session_state.pass_database:
                    user_data = st.session_state.pass_database[uid]
                    if pwd == user_data["pwd"]:
                        st.session_state.auth = True
                        st.session_state.user_role = user_data["role"]
                        st.session_state.user_type = user_data["type"]
                        st.session_state.expiration = user_data["activation"] + timedelta(days=user_data["duree_jours"])
                        st.rerun()
                    else: st.error("❌ Mot de passe incorrect.")
                else: st.error("❌ Identifiant ou numéro de Pass inconnu.")
            if st.button(t['btn_lost']): st.session_state.view = "reset"; st.rerun()
            if st.button(t['btn_create']): st.session_state.view = "signup"; st.rerun()

    elif st.session_state.view == "signup":
        st.subheader("Création de compte & Sélection du Pass initial")
        account_type = st.radio("Je suis :", ["Candidat (Pass 1 Jour Gratuit)", "Employeur (Pass 7 Jours Démo)"])
        st.text_input("Adresse Email")
        st.text_input("Choisir un mot de passe", type="password")
        if st.button("Activer mon compte & mon Pass d'essai"):
            st.success("Compte créé avec succès ! Connectez-vous."); st.session_state.view = "login"; st.rerun()

# --- INTERFACE APPLICATIVE MEMBRE ---
else:
    with st.sidebar:
        st.markdown(f"<h2 style='color:#FFFFFF;'>neocrm.zaxx</h2>", unsafe_allow_html=True)
        list_langs = LANG_SUPER_MANAGER if st.session_state.user_role == "SuperManager" else LANG_PUBLIC_ET_CLIENT
        st.selectbox("Langue / Language", list_langs, key="app_lang")
        st.divider()
        
        # Configuration dynamique des menus selon le profil
        if st.session_state.user_type in ["Employeur", "SuperUser"]:
            menu = st.radio("Menu Recruteur", ["Dashboard & Pass", "Rédaction d'offres IA", "Dispatch automatique", "Visioconférence Jitsi", "Mon Abonnement Pass"])
        else:
            menu = st.radio("Menu Candidat", ["Dashboard & Pass", "Amélioration CV & Lettre", "Testeur National ATS", "Templates CV Professionnels", "Visioconférence Jitsi", "Mon Abonnement Pass"])
        
        if st.button("🚪 Déconnexion"): st.session_state.auth = False; st.rerun()

    # --- PANNEAU COMMUN : DASHBOARD & ALERTES ---
    if menu == "Dashboard & Outils" or menu == "Dashboard & Pass":
        st.header(f"Espace de gestion — {st.session_state.user_type}")
        temps_restant = st.session_state.expiration - datetime.now()
        heures, restants = divmod(temps_restant.total_seconds(), 3600)
        st.markdown(f"<div class='pass-box'>⏱️ **Validité du Pass :** Il vous reste **{int(heures)} heures** d'accès total avant expiration.</div>", unsafe_allow_html=True)

    # --- MODULES EXCLUSIFS EMPLOYEURS ---
    elif menu == "Rédaction d'offres IA":
        st.header("✍️ Générateur d'offres d'emploi par Intelligence Artificielle")
        poste = st.text_input("Intitulé du poste recherché (ex: Ingénieur Commercial)")
        competences = st.text_area("Compétences clés indispensables")
        if st.button("Générer l'offre d'emploi optimisée"):
            st.markdown(f"""<div class='ai-box'><h3>Offre d'emploi : {poste}</h3><p>Nous recherchons un talent spécialisé en <b>{competences}</b> pour piloter nos projets stratégiques...</p><h4>Profil recherché :</h4><ul><li>Expérience confirmée</li><li>Maîtrise technologique avancée</li></ul></div>""", unsafe_allow_html=True)

    elif menu == "Dispatch automatique":
        st.header("⚡ Outil de Dispatch automatique de l'offre")
        st.write("Diffusez instantanément vos annonces éditées vers les canaux premium ciblés.")
        channels = st.multiselect("Sélectionnez les destinations de routage :", ["France Travail", "LinkedIn Jobs", "Indeed", "CVthèque Privée Zaxx", "Réseaux Commando"])
        if st.button("Lancer le dispatch de masse"):
            st.success(f"Multi-diffusion validée sur les canaux : {', '.join(channels)} (Routage instantané).")

    # --- MODULES EXCLUSIFS CANDIDATS ---
    elif menu == "Amélioration CV & Lettre":
        st.header("🤖 Relooking IA : CV & Lettre de Motivation")
        txt_cv = st.text_area("Copiez-collez le texte brut de votre CV actuel")
        txt_lm = st.text_area("Copiez-collez votre lettre de motivation")
        if st.button("Optimiser mes documents par l'IA"):
            st.markdown("""<div class='ai-box'><h3>✨ Vos documents relookés par notre IA</h3><b>CV Amélioré :</b> Structure réorganisée avec mots-clés optimisés à fort impact.<br><br><b>Lettre de motivation optimisée :</b> <p><i>'Madame, Monsieur, C’est avec un vif intérêt que je vous soumets ma candidature au poste... Mon expertise me permet de garantir une exécution rigoureuse...'</i></p></div>""", unsafe_allow_html=True)

    elif menu == "Testeur National ATS":
        st.header("📊 Simulateur de Score ATS (Robot de Recrutement)")
        st.write("Testez la conformité de votre CV face aux algorithmes de tri automatique.")
        if st.button("🎯 Évaluer mon CV d'origine"):
            st.session_state.ats_score = random.randint(35, 55)
        if st.session_state.ats_score:
            st.metric("Score ATS initial", f"{st.session_state.ats_score}%", help="Un score inférieur à 70% est généralement rejeté par les robots.")
            if st.session_state.ats_score < 60 and not st.session_state.ats_retested:
                st.warning("⚠️ Risque de rejet élevé. Utilisez les outils de relooking IA puis re-testez votre conformité.")
                if st.button("🔄 RE-TESTER APRÈS RELOOKING IA"):
                    st.session_state.ats_score = random.randint(85, 98)
                    st.session_state.ats_retested = True
                    st.rerun()
        if st.session_state.ats_retested:
            st.balloons()
            st.success("🚀 Score après optimisation validé !")

    elif menu == "Templates CV Professionnels":
        st.header("🎴 Modèles et Catalogues de CV Premium")
        st.write("Sélectionnez un visuel haut de gamme pour l'exportation de vos données.")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='cv-template'><b>🌌 Template Cyber-Blue</b><br><small>Idéal profils techniques</small></div>", unsafe_allow_html=True)
            st.button("Sélectionner Cyber", key="t1")
        with col2:
            st.markdown("<div class='cv-template'><b>👔 Template Executive Classic</b><br><small>Idéal managers</small></div>", unsafe_allow_html=True)
            st.button("Sélectionner Executive", key="t2")
        with col3:
            st.markdown("<div class='cv-template'><b>✨ Template Minimalist</b><br><small>Design épuré moderne</small></div>", unsafe_allow_html=True)
            st.button("Sélectionner Minimalist", key="t3")

    # --- VISIOCONFÉRENCE JITSI (DYNAMIQUE EMPLOYEUR/CANDIDAT) ---
    elif menu == "Visioconférence Jitsi":
        st.header("🎥 Planification & Salons d'entretien Vidéo (Jitsi)")
        
        if st.session_state.user_type in ["Employeur", "SuperUser"]:
            st.subheader("Espace Planification Recruteur")
            with st.form("form_planification"):
                d_date = st.date_input("Sélectionner la date", min_value=datetime.today())
                d_time = st.time_input("Sélectionner l'heure")
                if st.form_submit_button("Envoyer l'invitation au candidat"):
                    st.session_state.interview_session.update({"planned": True, "date": d_date, "time": d_time, "status": "En attente de confirmation du candidat"})
                    st.success("Invitation transmise.")
            
            if st.session_state.interview_session["planned"]:
                st.info(f"Rendez-vous envoyé pour le {st.session_state.interview_session['date']} à {st.session_state.interview_session['time']}. Statut : {st.session_state.interview_session['status']}")
                if st.session_state.interview_session["status"] == "Accepté par le candidat":
                    st.link_button("🚀 REJOINDRE LE SALON VIDEO JITSI", st.session_
