import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from supabase import create_client, Client
import requests

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="zipngo | IA & Recrutement Écosystème", layout="wide")

# --- INITIALISATION MULTI-SUPABASE & GROQ ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    
    # Connexion au dossier ZIP (Principal pour zipngo)
    ZIP_URL = st.secrets["ZIP_SUPABASE_URL"]
    ZIP_KEY = st.secrets["ZIP_SUPABASE_KEY"]
    supabase: Client = create_client(ZIP_URL, ZIP_KEY)
    
    # Connexion au dossier OP (Disponible en parallèle)
    OP_URL = st.secrets["OP_SUPABASE_URL"]
    OP_KEY = st.secrets["OP_SUPABASE_KEY"]
    supabase_op: Client = create_client(OP_URL, OP_KEY)
    
except Exception as e:
    st.error("⚠️ Erreur de configuration. Veuillez vérifier que vos 'Secrets' contiennent GROQ_API_KEY, les accès OP et les accès ZIP.")
    st.stop()

# --- MOTEUR DE TRAITEMENT REEL VIA GROQ API ---
def appeler_groq_ia(prompt_systeme, prompt_utilisateur):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": prompt_systeme},
            {"role": "user", "content": prompt_utilisateur}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Erreur API Groq (Code {response.status_code}) : Impossible de générer la réponse."
    except Exception as e:
        return f"Erreur de connexion réseau à l'IA : {str(e)}"

# --- SYSTÈME DE LANGUES TRADUITES (20 LANGUES TOTALES) ---
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
        "intro": "El océano de RRHH de vanguardia para impulsar tu carrera y tus contrataciones.",
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
        "desc": "zipngo è la soluzione progettata pour ottimizzare il tuo CV, superare i filtri ATS, generare annunci con IA e pianificare colloqui in tempo reale.",
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
        "desc": "zipngo는 이력서 최적화, ATS 필터 통과, AI 채용 공고 생성 및 실시간 면접 예약을 위해 설계된 솔루ชั่น입니다.",
        "uid": "로그인 ID / 이메일 주소", "pwd": "비밀번호",
        "btn_login": "ZIPNGO 접속 / 활성화", "btn_lost": "비밀번호 분실", "btn_create": "계정 만들기"
    },
    "中文": {
        "intro": "助力职业发展与高效招聘的尖端 HR 生态系统。",
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
        "intro": "आपके करियरและ भर्ती को बढ़ावा देने के लिए अत्याधुनिक मानव संसाधन पारिस्थितिकी तंत्र।",
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
        "desc": "zipngo là giải pháp được thiết kế to tối ưu hóa CV, vượt qua bộ lọc ATS, tạo tin tuyển dụng bằng AI và lên lịch phỏng vấn thời gian thực.",
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

# --- CONSERVATION DES ETATS SANS REMISE A ZERO INTEMPESTIVE ---
if "ats_score" not in st.session_state: st.session_state.ats_score = None
if "ats_feedback" not in st.session_state: st.session_state.ats_feedback = ""
if "ats_retested" not in st.session_state: st.session_state.ats_retested = False
if "auth" not in st.session_state: st.session_state.auth = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_role" not in st.session_state: st.session_state.user_role = None
if "user_type" not in st.session_state: st.session_state.user_type = None
if "expiration" not in st.session_state: st.session_state.expiration = None
if "view" not in st.session_state: st.session_state.view = "login"

# --- APPLICATION DU DESIGN PREMIUM ZIPNGO ---
def apply_premium_theme():
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
        .ai-box { padding: 20px; background-color: #F0F4F8; border-radius: 8px; border-left: 5px solid #1A237E; margin: 15px 0; white-space: pre-wrap; font-family: sans-serif; line-height: 1.5; color: #1A237E; }
        .cv-template { padding: 15px; border: 1px dashed #1A237E; border-radius: 6px; background: #FFF; text-align: center; margin-bottom: 10px; }
        .footer { text-align: center; padding: 25px; border-top: 1px solid #E2E8F0; margin-top: 50px; }
        .legal-link { color: #64748b; text-decoration: none; font-size: 11px; margin: 0 15px; }
    </style>
    """, unsafe_allow_html=True)

apply_premium_theme()

# --- VUES AUTHENTIFICATION ET ALLOCATION DES COMPTES (SUPABASE) ---
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
                            duree_jours = int(user_data.get("duree_jours
