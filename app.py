import streamlit as st

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Zipngo-Zaxx", page_icon="👍", layout="wide")

# --- 2. INJECTION DU DESIGN (LE CORRECTIF) ---
# Ce bloc dit à Streamlit : "Ceci n'est pas du texte, c'est du style"
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
    /* Logo et Titre */
    .main-logo-text { font-size: 65px !important; font-weight: 900; color: #002147; text-align: center; margin-bottom: 0px; text-transform: lowercase; letter-spacing: -2px; font-family: sans-serif; }
    .power-title { text-align: center; color: #00E5FF; font-size: 22px; font-weight: 800; margin-top: -25px; text-transform: uppercase; letter-spacing: 2px; font-family: sans-serif; }

    /* Boutons Personnalisés */
    .stButton>button { 
        background-color: #002147 !important; 
        color: white !important; 
        border-radius: 10px !important; 
        border: none !important; 
        transition: 0.3s; 
        width: 100%; 
        font-weight: bold; 
        height: 45px; 
    }
    .stButton>button:hover { 
        background-color: #F3812B !important; 
        transform: scale(1.02); 
    }

    /* Footer Design */
    .footer-container { border-top: 1px solid #eee; margin-top: 50px; padding-top: 20px; }
    .footer-text { font-size: 12px; color: #888888; text-align: center; font-family: sans-serif; }
    .footer-icon { color: #F3812B; font-size: 20px; vertical-align: middle; margin-left: 8px; transition: 0.3s; text-decoration: none; }
    .footer-icon:hover { color: #002147; transform: scale(1.2); }

    /* Suppression bordures expander */
    .stExpander { border: none !important; box-shadow: none !important; background-color: transparent !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONTENU DE LA PAGE ---
# Langue
col_l, _ = st.columns([1, 2])
with col_l:
    sel_lang = st.selectbox("🌐 Language", ["Français 🇫🇷", "English 🇺🇸", "Malagasy 🇲🇬"])

# Affichage du Logo
st.markdown("<h1 style='text-align: center; color: #F3812B; font-size: 80px; margin-bottom:0;'>👍</h1>", unsafe_allow_html=True)
st.markdown('<p class="main-logo-text">zipngo</p>', unsafe_allow_html=True)
st.markdown('<p class="power-title">The Power of Choice</p>', unsafe_allow_html=True)

# Bouton de test pour voir si le style fonctionne
st.markdown("<br>", unsafe_allow_html=True)
if st.button("Tester le bouton 👍"):
    st.balloons()

# --- 4. FOOTER ---
st.markdown('<div class="footer-container"></div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)

with f1:
    with st.expander("⚖️ Mentions Légales"):
        st.write("Éditeur : RAKOTOBE Liliane.")

with f3:
    st.markdown(f"""
        <div class="footer-text">
            © 2026 <b>RAKOTOBE Liliane</b> | 
            <a href="mailto:creationsites06@gmail.com" class="footer-icon">
                <i class="fa-regular fa-envelope"></i>
            </a>
        </div>
    """, unsafe_allow_html=True)
