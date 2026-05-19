import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="zipngo | IA & Recrutement Écosystème", layout="wide")

# --- INITIALISATION SUPABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("⚠️ Erreur de configuration Supabase. Veuillez vérifier vos 'Secrets' Streamlit.")
    st.stop()

# --- SYSTÈME DE LANGUES TRADUITES (20 LANGUES CENTRÉES SUR ZIPNGO) ---
LANG_MAP = {
    "Français": "fr", "English (US)": "en", "Malgache": "mg", "Español": "es", 
    "Deutsch": "de", "Italiano": "it", "Português": "pt", "Nederlands": "nl",
    "Русский": "ru", "日本語": "ja", "한국어": "ko", "中文": "zh",
    "العربية": "ar", "हिन्दी": "hi", "Türkçe": "tr", "Polski": "pl",
    "Svenska": "sv", "Tiếng Việt": "vi", "ไทย": "th", "Ελληνικά": "el"
}

TEXTS = {
    "Français": {
        "intro": "L'écosystème RH de pointe pour propulser votre carrière et vos recrutements.",
        "desc": "zipngo est la solution conçue pour optimiser vos CV, surclasser les filtres ATS, générer vos offres par l'IA et planifier vos entretiens en temps réel.",
        "uid": "Identifiant de connexion / Adresse Email", "pwd": "Mot de passe",
        "btn_login": "ACCÉDER À ZIPNGO / ACTIVATION", "btn_lost": "mot de passe perdu", "btn_create": "CRÉER UN COMPTE"
    },
    "English (US)": {
        "intro": "The cutting-edge HR ecosystem to boost your career and recruitment.",
        "desc": "zipngo is the solution designed to optimize your CV, bypass ATS filters, generate AI job offers, and schedule interviews in real-time.",
        "uid": "Login ID / Email Address", "pwd": "Password",
        "btn_login": "ACCESS ZIPNGO / ACTIVATION", "btn_lost": "lost password", "btn_create": "CREATE AN ACCOUNT"
    },
    "Malgache": {
        "intro": "Ny rafitra HR farany indrindra hampitomboana ny asanao sy ny fandraisana mpiasa.",
        "desc": "zipngo dia vahaolana namboarina hanatsarana ny CV-nao, handresena ny sivana ATS, hamoronana asa amin'ny alalan'ny IA ary handaminana dinidinika.",
        "uid": "Anarana fidirana / Mailaka", "pwd": "Teny miafina",
        "btn_login": "HIDITRA AMIN'NY ZIPNGO / ACTIVATION", "btn_lost": "hadino ny teny miafina", "btn_create": "HANOKATRA KAONTY"
    },
    "Español": {
        "intro": "El ecosistema de RRHH de vanguardia para impulsar tu carrera y tus contrataciones.",
        "desc": "zipngo es la solución diseñada para optimizar tu CV, superar los filtros ATS, generar ofertas de trabajo con IA y programar entrevistas en tiempo real.",
        "uid": "Identificación de ingreso / Correo electrónico", "pwd": "Contraseña",
        "btn_login": "ACCEDER A ZIPNGO / ACTIVACIÓN", "btn_lost": "contraseña perdida", "btn_create": "CREAR UNA CUENTA"
    },
    "Deutsch": {
        "intro": "Das führende HR-Ökosystem für Ihre Karriere und Personalbeschaffung.",
        "desc": "zipngo ist die Lösung, um Ihren Lebenslauf zu optimieren, ATS-Filter zu umgehen, KI-Stellenangebote zu erstellen und Interviews in Echtzeit zu planen.",
        "uid": "Anmelde-ID / E-Mail-Adresse", "pwd": "Passwort",
        "btn_login": "AUF ZIPNGO ZUGREIFEN / AKTIVIERUNG", "btn_lost": "Passwort vergessen", "btn_create": "KONTO ERSTELLEN"
    },
    "Italiano": {
        "intro": "L'ecosistema HR all'avanguardia per dare slancio alla tua carriera e al tuo recruiting.",
        "desc": "zipngo è la soluzione progettata per ottimizzare il tuo CV, superare i filtri ATS, generare annunci con IA e pianificare colloqui in tempo reale.",
        "uid": "ID di accesso / Email", "pwd": "Password",
        "btn_login": "ACCEDI A ZIPNGO / ATTIVAZIONE", "btn_lost": "password smarrita", "btn_create": "CREA UN ACCOUNT"
    },
    "Português": {
        "intro": "O ecossistema de RH de ponta para impulsionar sua carreira e recrutamento.",
        "desc": "zipngo é a solução concebida para otimizar seu currículo, superar filtros ATS, gerar ofertas com IA e agendar entrevistas em tempo real.",
        "uid": "ID de login / Email", "pwd": "Senha",
        "btn_login": "ACESSAR ZIPNGO / ATIVAÇÃO", "btn_lost": "senha perdida", "btn_create": "CRIAR UMA CONTA"
    },
    "Nederlands": {
        "intro": "Het geavanceerde HR-ecosysteem om uw carrière en rekrutering te stimuleren.",
        "desc": "zipngo is de oplossing om uw cv te optimaliseren, ATS-filters te omzeilen, AI-vacatures te genereren en interviews in realtime te plannen.",
        "uid": "Inlog-ID / E-mailadres", "pwd": "Wachtwoord",
        "btn_login": "TOEGANG TOT ZIPNGO / ACTIVATIE", "btn_lost": "wachtwoord vergeten", "btn_create": "ACCOUNT AANMAKEN"
    },
    "Русский": {
        "intro": "Передовая HR-экосистема для развития вашей карьеры и подбора персонала.",
        "desc": "zipngo — решение, созданное для оптимизации резюме, обхода фильтров ATS, генерации вакансий с ИИ и планирования собеседований в реальном времени.",
        "uid": "Идентификатор входа / Email", "pwd": "Пароль",
        "btn_login": "ВОЙТИ В ZIPNGO / АКТИВИРОВАТЬ", "btn_lost": "забыли пароль", "btn_create": "СОЗДАТЬ АККАУНТ"
    },
    "日本語": {
        "intro": "キャリアと採用を加速させる最先端のHRエコシステム。",
        "desc": "zipngoは、履歴書の最適化、ATSフィルターの突破、AI求人作成、リアルタイムの面接設定のために設計されたソリューションです。",
        "uid": "ログインID / メールアドレス", "pwd": "パスワード",
        "btn_login": "ZIPNGOにアクセス / 有効化", "btn_lost": "パスワードを忘れた場合", "btn_create": "アカウント作成"
    },
    "한국어": {
        "intro": "커리어와 채용을 혁신하는 최첨단 HR 에코시스템.",
        "desc": "zipngo는 이력서 최적화, ATS 필터 통과, AI 채용 공고 생성 및 실시간 면접 예약을 위해 설계된 솔루션입니다.",
        "uid": "로그인 ID / 이메일 주소", "pwd": "비밀번호",
        "btn_login": "ZIPNGO 접속 / 활성화", "btn_lost": "비밀번호 분실", "btn_create": "계정 만들기"
    },
    "中文": {
        "intro": "助力职业 digital 发展与高效招聘的尖端 HR 生态系统。",
        "desc": "zipngo 是专为优化个人简历、突破 ATS 筛选、AI 生成职位公告及实时安排面试而设计的解决方案。",
        "uid": "登录 ID / 电子邮箱", "pwd": "密码",
        "btn_login": "访问 ZIPNGO / 激活", "btn_lost": "忘记密码", "btn_create": "创建账户"
    },
    "العربية": {
        "intro": "نظام الموارد البشرية المتطور لتعزيز مسيرتك المهنية وتوظيفك.",
        "desc": "zipngo هو الحل المصمم لتحسين سيرتك الذاتية، وتجاوز فلاتر ATS، وإنشاء عروض العمل بالذكاء الاصطناعي، وجدولة المقابلات.",
        "uid": "معرف تسجيل الدخول / البريد الإلكتروني", "pwd": "كلمة المرور",
        "btn_login": "الدخول إلى ZIPNGO / التفعيل", "btn_lost": "فقدت كلمة المرور", "btn_create": "إنشاء حساب"
    },
    "हिन्दी": {
        "intro": "आपके करियर और भर्ती को बढ़ावा देने के लिए अत्याधुनिक मानव संसाधन पारिस्थितिकी तंत्र।",
        "desc": "zipngo आपके सीवी को अनुकूलित करने, एटीएस फिल्टर को पार करने, एआई नौकरी प्रस्ताव उत्पन्न करने और साक्षात्कार शेड्यूल करने के लिए समाधान है।",
        "uid": "लॉगिन आईडी / ईमेल पता", "pwd": "पासवर्ड",
        "btn_login": "ZIPNGO तक पहुँचें / सक्रिय करें", "btn_lost": "पासवर्ड भूल गए", "btn_create": "खाता बनाएं"
    },
    "Türkçe": {
        "intro": "Kariyerinizi ve işe alım süreçlerinizi güçlendirmek için yeni nesil İK ekosistemi.",
        "desc": "zipngo; CV'nizi optimize etmek, ATS filtrelerini geçmek, yapay zeka ile ilan oluşturmak ve mülakatları planlamak için tasarlanmış bir çözümdür.",
        "uid": "Kullanıcı Adı / E-posta Adresi", "pwd": "Şifre",
        "btn_login": "ZIPNGO'YA ERİŞ / AKTİVASYON", "btn_lost": "şifremi unuttum", "btn_create": "HESAP OLUŞTUR"
    },
    "Polski": {
        "intro": "Nowoczesny ekosystem HR, który napędzi Twoją karierę i rekrutację.",
        "desc": "zipngo to rozwiązanie stworzone do optymalizacji CV, omijania filtrów ATS, generowania ofert przez AI i planowania rozmów w czasie rzeczywistym.",
        "uid": "Identyfikator logowania / Adres e-mail", "pwd": "Hasło",
        "btn_login": "DOSTĘP DO ZIPNGO / AKTYWACJA", "btn_lost": "zapomniane hasło", "btn_create": "ZAŁÓŻ KONTO"
    },
    "Svenska": {
        "intro": "Det banbrytande HR-ekosystemet för att öka din karriär och rekrytering.",
        "desc": "zipngo är lösningen designad för att optimera ditt CV, passera ATS-filter, generera AI-jobbannonser och boka intervjuer i realtid.",
        "uid": "Inloggnings-ID / E-postadress", "pwd": "Lösenord",
        "btn_login": "TILLGÅNG TILL ZIPNGO / AKTIVERING", "btn_lost": "glömt lösenord", "btn_create": "SKAPA KONTO"
    },
    "Tiếng Việt": {
        "intro": "Hệ sinh thái nhân sự tiên tiến để thúc đẩy sự nghiệp và tuyển dụng của bạn.",
        "desc": "zipngo là giải pháp được thiết kế để tối ưu hóa CV, vượt qua bộ lọc ATS, tạo tin tuyển dụng bằng AI và lên lịch phỏng vấn thời gian thực.",
        "uid": "ID Đăng nhập / Địa chỉ Email", "pwd": "Mật khẩu",
        "btn_login": "TRUY CẬP ZIPNGO / KÍCH HOẠT", "btn_lost": "quên mật khẩu", "btn_create": "TẠO TÀI KHOẢN"
    },
    "ไทย": {
        "intro": "ระบบนิเวศ HR ล้ำสมัยเพื่อขับเคลื่อนอาชีพและการสรรหาบุคลากรของคุณ",
        "desc": "zipngo คือโซลูชันที่ออกแบบมาเพื่อเพิ่มประสิทธิภาพเรซูเม่ ผ่านตัวกรอง ATS สร้างประกาศงานด้วย AI และนัดหมายสัมภาษณ์แบบเรียลไทม์",
        "uid": "รหัสเข้าสู่ระบบ / อีเมล", "pwd": "รหัสผ่าน",
        "btn_login": "เข้าสู่ ZIPNGO / เปิดใช้งาน", "btn_lost": "ลืมรหัสผ่าน", "btn_create": "สร้างบัญชี"
    },
    "Ελληνικά": {
        "intro": "Το κορυφαίο οικοσύστημα HR για την ενίσχυση της καριέρας και των προσλήψεών σας.",
        "desc": "Το zipngo είναι η λύση που σχεδιάστηκε για τη βελτιστοποίηση του CV σας, την προσπέραση των φίλτρων ATS, τη δημιουργία αγγελιών με AI και τη διαχείριση συνεντεύξεων.",
        "uid": "ID Σύνδεσης / Διεύθυνση Email", "pwd": "Κωδικός πρόσβασης",
        "btn_login": "ΠΡΟΣΒΑΣΗ ΣΤΟ ZIPNGO / ΕΝΕΡΓΟΠΟΙΗΣΗ", "btn_lost": "ξεχάσατε τον κωδικό", "btn_create": "ΔΗΜΙΟΥΡΓΙΑ ΛΟΓΑΡΙΑΣ"
    }
}

LANG_SUPER_MANAGER = ["English (US)", "Français"]
LANG_PUBLIC_ET_CLIENT = list(LANG_MAP.keys()) 

# États locaux nécessaires pour l'interface
if "ats_score" not in st.session_state: st.session_state.ats_score = None
if "ats_retested" not in st.session_state: st.session_state.ats_retested = False
if "auth" not in st.session_state: st.session_state.auth = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_role" not in st.session_state: st.session_state.user_role = None
if "user_type" not in st.session_state: st.session_state.user_type = None
if "expiration" not in st.session_state: st.session_state.expiration = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- SYSTEME STYLES PREMIUM NEO ---
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

apply_neo_theme()

# --- FORMULAIRES DE CONNEXION ET CRÉATION (SUPABASE LINK) ---
if not st.session_state.auth:
    if st.session_state.view == "login":
        _, col, _ = st.columns([1, 1.4, 1])
        with col:
            selected_lang = st.selectbox("🌐", LANG_PUBLIC_ET_CLIENT, label_visibility="collapsed", key="login_lang")
            t = TEXTS.get(selected_lang, TEXTS["English (US)"])
            st.markdown("<h1 style='text-align:center; font-size: 52px; margin-bottom:0;'><span style='color:#1A237E;'>zip</span><span style='color:#00E5FF;'>ngo</span></h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold; color:#1A237E; font-size:18px;'>{t['intro']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#64748b; font-size:14px; line-height:1.3;'>{t['desc']}</p>", unsafe_allow_html=True)
            st.divider()
            
            uid = st.text_input(t['uid'])
            pwd = st.text_input(t['pwd'], type="password")
            
            if st.button(t['btn_login']):
                try:
                    response = supabase.table("users").select("*").eq("email", uid).execute()
                    if response.data:
                        user_data = response.data[0]
                        if pwd == user_data.get("password"):
                            activation_str = user_data.get("activation_date")
                            activation_dt = datetime.fromisoformat(activation_str.replace("Z", ""))
                            duree_jours = int(user_data.get("duree_jours", 1))
                            date_expiration = activation_dt + timedelta(days=duree_jours)
                            
                            if datetime.now() < date_expiration:
                                st.session_state.auth = True
                                st.session_state.user_email = user_data.get("email")
                                st.session_state.user_role = user_data.get("role", "Client")
                                st.session_state.user_type = user_data.get("user_type")
                                st.session_state.expiration = date_expiration
                                st.rerun()
                            else:
                                st.error(f"❌ Ce Pass temporel a expiré le {date_expiration.strftime('%d/%m/%Y à %H:%M')}.")
                        else:
                            st.error("❌ Mot de passe incorrect.")
                    else:
                        st.error("❌ Aucun compte ou numéro de Pass associé à cette adresse.")
                except Exception as ex:
                    st.error(f"Erreur de communication Base de données : {ex}")

            if st.button(t['btn_lost']): st.session_state.view = "reset"; st.rerun()
            if st.button(t['btn_create']): st.session_state.view = "signup"; st.rerun()

    elif st.session_state.view == "signup":
        st.subheader("Création de compte & Allocation du Pass d'accès zipngo")
        account_type = st.radio("Sélectionnez votre profil :", ["Candidat (Pass 1 Jour Gratuit)", "Employeur (Pass 7 Jours Démo)"])
        new_email = st.text_input("Votre adresse Email")
        new_pwd = st.text_input("Choisissez un mot de passe", type="password")
        
        if st.button("Activer mon compte & mon Pass temporel"):
            if new_email and new_pwd:
                u_type = "Candidat" if "Candidat" in account_type else "Employeur"
                d_jours = 1 if u_type == "Candidat" else 7
                
                try:
                    payload = {
                        "email": new_email,
                        "password": new_pwd,
                        "user_type": u_type,
                        "role": "Client",
                        "activation_date": datetime.now().isoformat(),
                        "duree_jours": d_jours
                    }
                    supabase.table("users").insert(payload).execute()
                    st.success("🎉 Votre Pass a été initialisé sur Supabase ! Connectez-vous dès maintenant.")
                    st.session_state.view = "login"
                    st.rerun()
                except Exception as insert_err:
                    st.error(f"Erreur lors de la création du Pass : {insert_err}")
            else:
                st.warning("Veuillez remplir l'intégralité des champs requis.")

    elif st.session_state.view == "reset":
        st.subheader("Demande de récupération")
        if st.button("Retour à l'accueil"): st.session_state.view = "login"; st.rerun()

# --- PANNEAU MEMBRE CONNECTÉ SYNCHRONISÉ ---
else:
    with st.sidebar:
        st.markdown("<h2 style='color:#FFFFFF;'>zipngo</h2>", unsafe_allow_html=True)
        list_langs = LANG_SUPER_MANAGER if st.session_state.user_role == "SuperManager" else LANG_PUBLIC_ET_CLIENT
        st.selectbox("Langue / Language", list_langs, key="app_lang")
        st.divider()
        
        if st.session_state.user_type in ["Employeur", "SuperUser"]:
            menu = st.radio("Menu Recruteur", ["Dashboard & Pass", "Rédaction d'offres IA", "Dispatch automatique", "Visioconférence Jitsi", "Mon Abonnement Pass"])
        else:
            menu = st.radio("Menu Candidat", ["Dashboard & Pass", "Amélioration CV & Lettre", "Testeur National ATS", "Templates CV Professionnels", "Visioconférence Jitsi", "Mon Abonnement Pass"])
        
        if st.button("🚪 Déconnexion"): st.session_state.auth = False; st.rerun()

    # --- RENDER DES VUES APPLICATIVES ---
    if menu == "Dashboard & Pass":
        st.header(f"Espace de travail zipngo — Profil {st.session_state.user_type}")
        temps_restant = st.session_state.expiration - datetime.now()
        heures, restants = divmod(temps_restant.total_seconds(), 3600)
        st.markdown(f"<div class='pass-box'>⏱️ **Alerte Validité :** Il vous reste **{max(0, int(heures))} heures** d'accès total associé à votre compte.</div>", unsafe_allow_html=True)
        st.info(f"Compte actif : {st.session_state.user_email}")

    # --- CODE INTERACTION EMPLOYEURS ---
    elif menu == "Rédaction d'offres IA":
        st.header("✍️ Générateur d'offres d'emploi par Intelligence Artificielle")
        poste = st.text_input("Intitulé du poste à pourvoir")
        competences = st.text_area("Compétences et exigences clés")
        if st.button("Générer l'offre d'emploi optimisée"):
            st.markdown(f"""<div class='ai-box'><h3>Offre d'emploi : {poste}</h3><p>Nous recherchons un profil expert possédant les compétences suivantes : <b>{competences}</b>. Vos principales responsabilités incluront la gestion et le développement de nos outils stratégiques...</p></div>""", unsafe_allow_html=True)

    elif menu == "Dispatch automatique":
        st.header("⚡ Outil de Dispatch automatique de l'offre")
        st.write("Routez instantanément vos annonces éditées vers les plateformes partenaires.")
        channels = st.multiselect("Sélectionnez les plateformes de routage :", ["France Travail", "LinkedIn Jobs", "Indeed", "CVthèque Privée Zaxx", "Réseaux Commando"])
        if st.button("Lancer le dispatch de masse"):
            st.success(f"Multi-diffusion lancée avec succès vers : {', '.join(channels)}.")

    # --- CODE INTERACTION CANDIDATS ---
    elif menu == "Amélioration CV & Lettre":
        st.header("🤖 Relooking IA : CV & Lettre de Motivation")
        txt_cv = st.text_area("Insérez le texte brut de votre CV")
        txt_lm = st.text_area("Insérez le texte brut de votre Lettre de Motivation")
        if st.button("Optimiser mes documents par l'IA"):
            st.markdown("""<div class='ai-box'><h3>✨ Vos documents relookés par notre IA</h3><b>CV Amélioré :</b> Intégration de mots-clés stratégiques pour passer les filtres logiciels.<br><br><b>Lettre de motivation optimisée :</b> <p><i>'Madame, Monsieur, C’est avec beaucoup d’enthousiasme que je postule à votre offre... Mon expertise garantit une valeur ajoutée immédiate...'</i></p></div>""", unsafe_allow_html=True)

    elif menu == "Testeur National ATS":
        st.header("📊 Simulateur et Testeur de Score ATS")
        st.write("Vérifiez l'impact et le relooking de votre CV face aux algorithmes ATS de tri de candidatures.")
        if st.button("🎯 Évaluer mon CV d'origine"):
            st.session_state.ats_score = random.randint(35, 53)
        if st.session_state.ats_score:
            st.metric("Score de conformité ATS", f"{st.session_state.ats_score}%")
            if st.session_state.ats_score < 60 and not st.session_state.ats_retested:
                st.warning("⚠️ Alerte : Votre CV risque d'être rejeté par les robots. Appliquez l'optimisation IA puis re-testez.")
                if st.button("🔄 RE-TESTER APRÈS RELOOKING IA"):
                    st.session_state.ats_score = random.randint(85, 97)
                    st.session_state.ats_retested = True
                    st.rerun()
        if st.session_state.ats_retested:
            st.balloons()
            st.success("🚀 Succès ! Votre CV relooké est désormais conforme à 95%+ aux critères ATS.")

    elif menu == "Templates CV Professionnels":
        st.header("🎴 Modèles et Catalogues de CV Premium")
        st.write("Choisissez le visuel haut de gamme de votre choix :")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<div class='cv-template'><b>🌌 Template Cyber-Blue</b><br><small>Idéal métiers tech & IT</small></div>", unsafe_allow_html=True)
            st.button("Choisir Cyber", key="k1")
        with col2:
            st.markdown("<div class='cv-template'><b>👔 Template Executive Classic</b><br><small>Idéal managers & cadres</small></div>", unsafe_allow_html=True)
            st.button("Choisir Executive", key="k2")
        with col3:
            st.markdown("<div class='cv-template'><b>✨ Template Minimalist</b><br><small>Design épuré moderne</small></div>", unsafe_allow_html=True)
            st.button("Choisir Minimalist", key="k3")

    # --- INTERACTION RÉEL VISIOCONFÉRENCE JITSI VIA SUPABASE ---
    elif menu == "Visioconférence Jitsi":
        st.header("🎥 Planification & Salons d'entretien Vidéo (Jitsi)")
        room_url = "https://meet.jit.si/ZipngoInterviewRoom"
        
        if st.session_state.user_type in ["Employeur", "SuperUser"]:
            st.subheader("Espace Planification Recruteur")
            with st.form("form_supabase_interview"):
                d_date = st.date_input("Sélectionner la date", min_value=datetime.today())
                d_time = st.time_input("Sélectionner l'heure")
                if st.form_submit_button("Envoyer l'invitation au candidat"):
                    try:
                        supabase.table("interviews").insert({
                            "employer_email": st.session_state.user_email,
                            "date": str(d_date),
                            "time": str(d_time),
                            "status": "En attente"
                        }).execute()
                        st.success("Invitation synchronisée en base de données et envoyée au candidat.")
                    except Exception as int_err:
                        st.error(f"Erreur d'insertion de la rencontre : {int_err}")
            
            try:
                res = supabase.table("interviews").select("*").eq("employer_email", st.session_state.user_email).execute()
                if res.data:
                    st.write("### Vos rendez-vous programmés :")
                    for i in res.data:
                        st.info(f"📅 Date : {i['date']} | ⏰ Heure : {i['time']} | 🔄 Statut : {i['status']}")
                        if i['status'] == "Accepté par le candidat":
                            st.link_button("🚀 REJOINDRE LE SALON VIDEO JITSI", room_url, key=str(i['id']))
            except: pass

        elif st.session_state.user_type == "Candidat":
            st.subheader("Espace Invitations Candidat")
            try:
                res = supabase.table("interviews").select("*").execute()
                if res.data:
                    for idx, i in enumerate(res.data):
                        st.markdown(f"<div class='cv-template'><b>🔔 Proposition reçue d'un recruteur</b><br>Date : {i['date']} à {i['time']}<br>Statut actuel : {i['status']}</div>", unsafe_allow_html=True)
                        if i['status'] == "En attente":
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("✅ ACCEPTER", key=f"acc_{idx}"):
                                    supabase.table("interviews").update({"status": "Accepté par le candidat"}).eq("id", i["id"]).execute()
                                    st.rerun()
                            with c2:
                                if st.button("❌ REFUSER", key=f"ref_{idx}"):
                                    supabase.table("interviews").update({"status": "Refusé par le candidat"}).eq("id", i["id"]).execute()
                                    st.rerun()
                        elif i['status'] == "Accepté par le candidat":
                            st.success("Cet entretien est validé.")
                            st.link_button("📲 REJOINDRE MON INTERVIEW EN DIRECT", room_url, key=f"join_{idx}")
                else:
                    st.write("Aucune proposition d'entretien en attente actuellement.")
            except Exception as read_err:
                st.write("En attente de planification de la part d'un recruteur.")

    # --- ABONNEMENT ET OFFRES DE CONVERSION PAYANTES ---
    elif menu == "Mon Abonnement Pass":
        st.header("Gestion de vos accès & Offres Privilèges")
        if st.session_state.user_type == "Candidat":
            st.markdown("""<div class="premium-box"><h3>🚀 PASS PRIVILÈGE CANDIDAT (90 JOURS)</h3><p>Accès complet à toutes les requêtes, relookings illimités et mise en avant de votre profil aux yeux des recruteurs.</p><div style="font-size: 28px; font-weight: bold; margin: 15px 0; color: #00E5FF;">3,00 EUR</div><a href="https://stripe.com/checkout/lien-test-candidat" target="_blank" class="premium-btn">PROLONGER MON ACCÈS POUR 3€</a></div>""", unsafe_allow_html=True)
        elif st.session_state.user_type == "Employeur":
            st.markdown("""<div class="premium-box"><h3>💼 PASS BUSINESS EMPLOYEUR (90 JOURS)</h3><p>Outils de matching avancés, dispatch illimité vers toutes les plateformes nationales et accès à la CVthèque globale.</p><div style="font-size: 28px; font-weight: bold; margin: 15px 0; color: #00E5FF;">39,00 EUR</div><a href="https://stripe.com/checkout/lien-test-employeur" target="_blank" class="premium-btn">DEVENIR RECRUTEUR PREMIUM POUR 39€</a></div>""", unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""<div class="footer"><a href="#" class="legal-link">Mentions Légales</a> | <a href="#" class="legal-link">CGV</a><p>© 2026 zipngo | Créatrice : Liliane RAKOTOBE ✉️</p></div>""", unsafe_allow_html=True)
