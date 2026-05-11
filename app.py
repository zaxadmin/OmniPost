import streamlit as st
from supabase import create_client
from ai_engine import coach_ia, generate_offer
from datetime import datetime, timedelta

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin-bottom: 0px; text-transform: lowercase; letter-spacing: -2px; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; }
    .feature-card { background-color: #FFFFFF; padding: 25px; border-radius: 15px; border: 1px solid #e1f5fe; box-shadow: 0 10px 20px rgba(0, 33, 71, 0.05); height: 100%; text-align: center; }
    .price-tag { background-color: #002147; color: #00E5FF; padding: 10px 20px; border-radius: 20px; font-weight: bold; display: inline-block; margin: 15px 0; }
    .fake-payment { background-color: #f0f7ff; border: 2px dashed #002147; padding: 20px; border-radius: 10px; margin: 20px 0; }
    .stButton>button { background-color: #002147 !important; color: white !important; border-radius: 10px !important; border: none !important; transition: 0.3s; width: 100%; font-weight: bold; height: 45px; }
    .stButton>button:hover { background-color: #F3812B !important; transform: scale(1.01); }
    .footer-text { font-size: 11px; color: #888888; text-align: center; padding: 10px; }
    .footer-icon { color: #F3812B; font-size: 16px; vertical-align: middle; margin-left: 5px; transition: 0.3s; }
    .footer-icon:hover { transform: scale(1.2); color: #002147; }
    .stExpander { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LANGUES ---
LANGS = {
    "Français 🇫🇷": "French", "English 🇺🇸": "English", "Malagasy 🇲🇬": "Malagasy", 
    "Español 🇪🇸": "Spanish", "Deutsch 🇩🇪": "German", "Italiano 🇮🇹": "Italian", 
    "Português 🇧🇷": "Portuguese", "Русский 🇷🇺": "Russian", "日本語 🇯🇵": "Japanese", 
    "العربية 🇸🇦": "Arabic", "Türkçe 🇹🇷": "Turkish", "Nederlands 🇳🇱": "Dutch",
    "한국어 🇰🇷": "Korean", "中文 🇨🇳": "Chinese", "हिन्दी 🇮🇳": "Hindi", 
    "Polski 🇵🇱": "Polish", "Svenska 🇸🇪": "Swedish", "Tiếng Việt 🇻🇳": "Vietnamese",
    "Bahasa Indonesia 🇮🇩": "Indonesian", "ไทย 🇹🇭": "Thai"
}

# --- 3. CONNEXIONS ---
supabase_auth = create_client(st.secrets["ZIP_URL"], st.secrets["ZIP_SERVICE_KEY"])
supabase_data = create_client(st.secrets["OP_URL"], st.secrets["OP_SERVICE_KEY"])

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. ACCUEIL ---
if not st.session_state.user:
    st.markdown("<h1 style='text-align: center; margin-bottom: 0; color: #F3812B; font-size: 80px;'>👍</h1>", unsafe_allow_html=True)
    st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
    st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="feature-card"><h2 style="color:#002147;">Candidat</h2><p>Essai 1 jour : 1 relooking complet et 1 test ATS.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="feature-card"><h2 style="color:#002147;">Employeur</h2><p>Essai 7 jours : Accès complet base talents et visio.</p></div>', unsafe_allow_html=True)

    t_log, t_reg = st.tabs(["🔑 Connexion", "📝 Création de compte"])
    with t_reg:
        re, rp = st.text_input("Email", key="re"), st.text_input("Mot de passe", type="password", key="rp")
        rr = st.radio("Je suis un :", ["Candidat", "Employeur"], horizontal=True)
        if st.button("Démarrer mon essai 👍"):
            days = 1 if rr == "Candidat" else 7
            exp = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            supabase_auth.table("users").insert({"email": re, "password": rp, "role": rr, "expire_at": exp, "status": "essai", "tokens_ia": 1}).execute()
            st.success(f"Compte créé ! Expire le {exp}.")

    with t_log:
        le, lp = st.text_input("Email", key="le"), st.text_input("Pass", type="password", key="lp")
        if st.button("Entrer 👍"):
            res = supabase_auth.table("users").select("*").eq("email", le).eq("password", lp).execute()
            if res.data:
                u = res.data[0]
                st.session_state.user, st.session_state.role, st.session_state.expire_at = le, u['role'], u['expire_at']
                st.session_state.status, st.session_state.tokens = u['status'], u.get('tokens_ia', 0)
                st.rerun()

# --- 5. DASHBOARD ---
else:
    is_expired = datetime.strptime(st.session_state.expire_at, '%Y-%m-%d') < datetime.now()
    with st.sidebar:
        st.markdown('<p style="font-size:30px; font-weight:900; color:#002147;">zaxx</p>', unsafe_allow_html=True)
        st.write(f"👤 {st.session_state.user}")
        if is_expired: st.error("⌛ Accès expiré")
        else: st.info(f"⏳ Fin d'accès : {st.session_state.expire_at}")
        sel_lang = st.selectbox("🌐 Langue IA", list(LANGS.keys()))
        st.divider()
        if st.button("❌ Supprimer mon compte"):
            if st.checkbox("Confirmer la suppression"):
                supabase_auth.table("users").delete().eq("email", st.session_state.user).execute()
                st.session_state.user = None
                st.rerun()
        if st.button("Déconnexion"):
            st.session_state.user = None
            st.rerun()

    if st.session_state.role == "Candidat":
        t1, t2, t3 = st.tabs(["🎥 Entretiens", "🪄 Services IA", "💳 Activer 3 mois"])
        with t2:
            if is_expired and st.session_state.status == "essai":
                st.warning("Essai terminé. Activez l'accès complet.")
            else:
                st.subheader(f"Relooking & ATS ({sel_lang})")
                st.write(f"Crédits : {st.session_state.tokens}")
                cv_file = st.file_uploader("Uploader CV/Lettre")
                if st.button("Lancer l'IA 👍") and st.session_state.tokens > 0:
                    st.write("Analyse...")
                    if st.session_state.status == "essai":
                        supabase_auth.table("users").update({"tokens_ia": 0}).eq("email", st.session_state.user).execute()
                        st.session_state.tokens = 0
        with t3:
            st.subheader("Accès complet 90 jours")
            st.markdown('<div class="price-tag">Tarif : 3€</div>', unsafe_allow_html=True)
            st.markdown('<div class="fake-payment">💳 <b>Paiement Virtuel</b><br>Accès unique. Pas de prélèvement automatique.</div>', unsafe_allow_html=True)
            if st.button("Activer 👍"):
                new_exp = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                supabase_auth.table("users").update({"expire_at": new_exp, "status": "premium", "tokens_ia": 999}).eq("email", st.session_state.user).execute()
                st.session_state.expire_at, st.session_state.status = new_exp, "premium"
                st.rerun()
    else: # EMPLOYEUR
        t1, t2, t3 = st.tabs(["🔍 Recherche", "📅 Visio", "💳 Activer 3 mois"])
        with t3:
            st.subheader("Accès Recruteur")
            st.markdown('<div class="price-tag">Tarif : 49€</div>', unsafe_allow_html=True)
            st.markdown('<div class="fake-payment">💳 <b>Paiement Entreprise</b><br>Accès 90 jours.</div>', unsafe_allow_html=True)
            if st.button("Activer l'accès 👍"):
                new_exp = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                supabase_auth.table("users").update({"expire_at": new_exp, "status": "premium"}).eq("email", st.session_state.user).execute()
                st.session_state.expire_at, st.session_state.status = new_exp, "premium"
                st.rerun()

# --- 6. FOOTER ---
st.divider()
f1, f2, f3 = st.columns(3)
with f1:
    with st.expander("⚖️ Mentions Légales"):
        st.write("Éditeur : RAKOTOBE Liliane. Hébergement : Streamlit Cloud.")
with f2:
    with st.expander("📜 CGV"):
        st.write("Produit virtuel numérique. Pas de remboursement après accès au service.")
with f3:
    st.markdown(f'<div class="footer-text">© 2026 <b>RAKOTOBE Liliane</b> | <a href="mailto:creationsites06@gmail.com"><i class="fa-regular fa-envelope footer-icon"></i></a></div>', unsafe_allow_html=True)
