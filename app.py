import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="neocrm.zaxx | Supabase Enterprise Ecosystem", layout="wide")

# --- INITIALISATION SUPABASE ---
# Récupération sécurisée des identifiants depuis les Secrets Streamlit
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("⚠️ Erreur de configuration Supabase. Veuillez vérifier vos 'Secrets' Streamlit.")
    st.stop()

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
        "uid": "Identifiant de connexion / Adresse Email", "pwd": "Mot de passe",
        "btn_login": "ACCÉDER À MON CRM / ACTIVATION", "btn_lost": "mots de passe perdu", "btn_create": "CREER UN COMPTE"
    },
    "English (US)": {
        "intro": "The cutting-edge CRM ecosystem to boost your sales.",
        "desc": "neocrm.zaxx is the solution we designed to centralize commercial intelligence, optimize conversions, and collaborate in real-time.",
        "uid": "Login ID / Email Address", "pwd": "Password",
        "btn_login": "ACCESS MY CRM / ACTIVATION", "btn_lost": "lost password", "btn_create": "CREATE AN ACCOUNT"
    },
    "Malgache": {
        "intro": "Ny rafitra CRM farany indrindra hampitomboana ny fivarotanao.",
        "desc": "neocrm.zaxx dia vahaolana namboarinay hanambarana ny fahaiza-manao ara-barotra sy hiaraha-miasa amin'ny fotoana tena izy.",
        "uid": "Anarana fidirana / Mailaka", "pwd": "Teny miafina",
        "btn_login": "HIDITRA AMIN'NY CRM / ACTIVATION", "btn_lost": "hadino ny teny miafina", "btn_create": "HANOKATRA KAONTY"
    },
    "Español": {
        "intro": "El ecosistema CRM de vanguardia para impulsar sus ventas.",
        "desc": "neocrm.zaxx es la solución diseñada para centralizar la inteligencia comercial, optimizar conversiones y colaborar en tiempo real.",
        "uid": "Identificación de ingreso / Correo electrónico", "pwd": "Contraseña",
        "btn_login": "ACCEDER A MI CRM / ACTIVACIÓN", "btn_lost": "contraseña perdida", "btn_create": "CREAR UNA CUENTA"
    },
    "Deutsch": {
        "intro": "Das führende CRM-Ökosystem zur Steigerung Ihres Umsatzes.",
        "desc": "neocrm.zaxx ist die Lösung, die wir entwickelt haben, um Vertriebsintelligenz zu zentralisieren, Conversions zu optimieren und in Echtzeit zusammenzuarbeiten.",
        "uid": "Anmelde-ID / E-Mail-Adresse", "pwd": "Passwort",
        "btn_login": "AUF MEIN CRM ZUGREIFEN / AKTIVIERUNG", "btn_lost": "Passwort vergessen", "btn_create": "KONTO ERSTELLEN"
    },
    "Italiano": {
        "intro": "L'ecosistema CRM all'avanguardia per incrementare le tue vendite.",
        "desc": "neocrm.zaxx è la soluzione progettata per centralizzare l'intelligence commerciale, ottimizzare le conversioni e collaborer in tempo reale.",
        "uid": "ID di accesso / Email", "pwd": "Password",
        "btn_login": "ACCEDI AL MIO CRM / ATTIVAZIONE", "btn_lost": "password smarrita", "btn_create": "CREA UN ACCOUNT"
    },
    "Português": {
        "intro": "O ecossistema CRM de ponta para impulsionar suas vendas.",
        "desc": "neocrm.zaxx é a solução que concebemos para centralizar a inteligência comercial, otimizar conversões e colaborar em tempo real.",
        "uid": "ID de login / Email", "pwd": "Senha",
        "btn_login": "ACESSAR MEU CRM / ATIVAÇÃO", "btn_lost": "senha perdida", "btn_create": "CRIAR UMA CONTA"
    },
    "Nederlands": {
        "intro": "Het geavanceerde CRM-ecosysteem om uw verkoop te stimuleren.",
        "desc": "neocrm.zaxx is de oplossing die we hebben ontworpen om commerciële intelligentie te centraliseren, conversies te optimaliseren en in realtime samen te werken.",
        "uid": "Inlog-ID / E-mailadres", "pwd": "Wachtwoord",
        "btn_login": "TOEGANG TOT MIJN CRM / ACTIVATIE", "btn_lost": "wachtwoord vergeten", "btn_create": "ACCOUNT AANMAKEN"
    },
    "Русский": {
        "intro": "Передовая экосистема CRM для стимулирования ваших продаж.",
        "desc": "neocrm.zaxx — это решение, разработанное нами для централизации коммерческой аналитики, оптимизации конверсий и совместной работы в реальном времени.",
        "uid": "Идентификатор входа / Email", "pwd": "Пароль",
        "btn_login": "ВОЙТИ В МОЙ CRM / АКТИВАЦИЯ", "btn_lost": "забыли пароль", "btn_create": "СОЗДАТЬ АККАУНТ"
    },
    "日本語": {
        "intro": "売上を伸ばすための最先端のCRMエコシステム。",
        "desc": "neocrm.zaxxは、営業インテリジェンスの集中化、コンバージョンの最適化、リアルタイムのコラボレーションのために設計されたソリューションです。",
        "uid": "ログインID / メールアドレス", "pwd": "パスワード",
        "btn_login": "CRMにアクセス / アクティベーション", "btn_lost": "パスワードを忘れた場合", "btn_create": "アカウント作成"
    },
    "한국어": {
        "intro": "매출 증대를 위한 최첨단 CRM 에코시스템.",
        "desc": "neocrm.zaxx는 영업 인텔리전스를 중앙화하고 전환을 최적화하며 실시간으로 협업할 수 있도록 설계된 솔루션입니다.",
        "uid": "로그인 ID / 이메일 주소", "pwd": "비밀번호",
        "btn_login": "내 CRM 액세스 / 활성화", "btn_lost": "비밀번호를 잊으셨나요", "btn_create": "계정 만들기"
    },
    "中文": {
        "intro": "助力销售增长的尖端 CRM 生态系统。",
        "desc": "neocrm.zaxx 是我们专为集中商业智能、优化转化和实时协作而设计的解决方案。",
        "uid": "登录 ID / 电子邮箱", "pwd": "密码",
        "btn_login": "访问 my CRM / 激活", "btn_lost": "忘记密码", "btn_create": "创建账户"
    },
    "العربية": {
        "intro": "نظام CRM المتطور لتعزيز مبيعاتك.",
        "desc": "neocrm.zaxx هو الحل الذي صممناه لمركزية الذكاء التجاري، وتحسين التحويلات، والتعاون في الوقت الفعلي.",
        "uid": "معرف تسجيل الدخول / البريد الإلكتروني", "pwd": "كلمة المرور",
        "btn_login": "الوصول إلى CRM الخاص بي / التفعيل", "btn_lost": "فقدت كلمة المرور", "btn_create": "إنشاء حساب"
    },
    "हिन्दी": {
        "intro": "आपकी बिक्री बढ़ाने के लिए अत्याधुनिक CRM पारिस्थितिकी तंत्र।",
        "desc": "neocrm.zaxx वाणिज्यिक खुफिया जानकारी को केंद्रीकृत करने, रूपांतरणों को अनुकूलित करने और वास्तविक समय में सहयोग करने के लिए हमारे द्वारा डिज़ाइन किया गया समाधान है।",
        "uid": "लॉगิน आईडी / ईमेल पता", "pwd": "पासवर्ड",
        "btn_login": "मेरे CRM तक पहुँचें / सक्रियण", "btn_lost": "पासवर्ड भूल गए", "btn_create": "खाता बनाएं"
    },
    "Türkçe": {
        "intro": "Satışlarınızı artırmak için en son teknoloji CRM ekosistemi.",
        "desc": "neocrm.zaxx, ticari zekayı merkezileştirmek, dönüşümleri optimize etmek ve gerçek zamanlı iş birliği yapmak için tasarladığımız çözümdür.",
        "uid": "Kullanıcı Adı / E-posta Adresi", "pwd": "Şifre",
        "btn_login": "CRM'İME ERİŞ / AKTİVASYON", "btn_lost": "şifremi unuttum", "btn_create": "HESAP OLUŞTUR"
    },
    "Polski": {
        "intro": "Nowoczesny ekosystem CRM, który napędzi Twoją sprzedaż.",
        "desc": "neocrm.zaxx to rozwiązanie zaprojektowane w celu centralizacji danych handlowych, optymalizacji konwersji i współpracy w czasie rzeczywistym.",
        "uid": "Identyfikator logowania / Adres e-mail", "pwd": "Hasło",
        "btn_login": "DOSTĘP DO MOJEGO CRM / AKTYWACJA", "btn_lost": "zapomniane hasło", "btn_create": "ZAŁÓŻ KONTO"
    },
    "Svenska": {
        "intro": "Det banbrytande CRM-ekosystemet för att öka din försäljning.",
        "desc": "neocrm.zaxx är lösningen vi designat för att centralisera affärsintelligens, optimera konverteringar och samarbeta i realtid.",
        "uid": "Inloggnings-ID / E-postadress", "pwd": "Lösenord",
        "btn_login": "TILLGÅNG TILL MITT CRM / AKTIVERING", "btn_lost": "glömt lösenord", "btn_create": "SKAPA KONTO"
    },
    "Tiếng Việt": {
        "intro": "Hệ sinh thái CRM tiên tiến để thúc đẩy doanh số bán hàng của bạn.",
        "desc": "neocrm.zaxx là giải pháp chúng tôi thiết kế để tập trung trí tuệ thương mại, tối ưu hóa chuyển đổi và cộng tác trong thời gian thực.",
        "uid": "ID Đăng nhập / Địa chỉ Email", "pwd": "Mật khẩu",
        "btn_login": "TRUY CẬP CRM CỦA TÔI / KÍCH HOẠT", "btn_lost": "quên mật khẩu", "btn_create": "TẠO TÀI KHOẢN"
    },
    "ไทย": {
        "intro": "ระบบนิเวศ CRM ที่ล้ำสมัยเพื่อเพิ่มยอดขายของคุณ",
        "desc": "neocrm.zaxx คือโซลูชันที่เราออกแบบมาเพื่อรวมศูนย์ข้อมูลเชิงลึกทางการค้า เพิ่มประสิทธิภาพการแปลง และทำงานร่วมกันแบบเรียลไทม์",
        "uid": "รหัสเข้าสู่ระบบ / อีเมล", "pwd": "รหัสผ่าน",
        "btn_login": "เข้าสู่ระบบ CRM / เปิดใช้งาน", "btn_lost": "ลืมรหัสผ่าน", "btn_create": "สร้างบัญชี"
    },
    "Ελληνικά": {
        "intro": "Το κορυφαίο οικοσύστημα CRM για την ενίσχυση των πωλήσεών σας.",
        "desc": "Το neocrm.zaxx είναι η λύση που σχεδιάσαμε για τη συγκέντρωση της εμπορικής ευφυΐας, τη βελτιστοποίηση των μετατροπών και τη συνεργασία σε πραγματικό χρόνο.",
        "uid": "ID Σύνδεσης / Διεύθυνση Email", "pwd": "Κωδικός πρόσβασης",
        "btn_login": "ΠΡΟΣΒΑΣΗ ΣΤΟ CRM ΜΟΥ / ΕΝΕΡΓΟΠΟΙΗΣΗ", "btn_lost": "ξεχάσατε τον κωδικό", "btn_create": "ΔΗΜΙ
