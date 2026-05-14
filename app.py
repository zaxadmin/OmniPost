import streamlit as st
import pandas as pd

# --- 1. LOGO EN PUR CSS/HTML (ZÉRO IMAGE, ZÉRO BASE64) ---
def display_logo_zip_css():
    logo_html = """
    <div style="
        text-align: center; 
        padding: 20px; 
        font-family: 'Arial Black', sans-serif;
        background: linear-gradient(145deg, #0f172a, #1e293b);
        border: 2px solid #FFD700;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
        margin-bottom: 25px;">
        <span style="color: #FFFFFF; font-size: 28px; letter-spacing: -1px;">zip</span>
        <span style="color: #FFD700; font-size: 28px; font-weight: 900;">ngo</span>
        <div style="color: #FFD700; font-size: 12px; margin-top: -5px; letter-spacing: 3px; font-weight: bold;">
            .ZAXX
        </div>
    </div>
    """
    return logo_html

# --- 2. CONFIGURATION & DESIGN GLOBAL ---
st.set_page_config(page_title="zipngo.zaxx", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0A0F1E; color: #FFFFFF; }
    
    /* Textes et Labels */
    .stWidget label, p, .stMarkdown, .stRadio label { 
        color: #FFFFFF !important; 
        font-weight: 600 !important; 
    }
    
    /* Champs de saisie zipngo (Thème Or/Jaune) */
    .stTextInput input, .stSelectbox div { 
        background-color: #161B22 !important; 
        color: white !important; 
        border: 1px solid #FFD700 !important; 
    }

    /* Boutons Commando Or */
    .stButton>button { 
        background: linear-gradient(90deg, #FFD700, #B8860B) !important; 
        color: #0A0F1E !important; 
        font-weight: 800; 
        border-radius: 8px; 
        border: none;
    }

    /* Masquage des données sensibles */
    .masked { 
        filter: blur(6px); 
        background: #30363D; 
        padding: 2px 6px; 
        border-radius: 4px; 
        user-select: none; 
    }
</style>
""", unsafe_allow_html=True)

# --- 3. RÈGLES DE COMMISSION COMMANDO (ADMIN ZAXX) ---
COMMANDO_RULES = {
    "teleprospecteur": {"fixe": 15.0, "label": "Téléprospecteur (15%)"},
    "expert": {"fixe": 17.0, "label": "Télépro Expert (17%)"},
    "manager": {"fixe": 15.0, "prime_global": 10.0, "label": "Manager (15% + 10% CA Global)"},
    "supermanager": {"fixe": 35.0, "label": "Super Manager (35%)"}
}

# --- 4. GESTION DES LANGUES ---
# 20 langues pour l'interface client, 3 pour le commando
ZIP_LANGS = ["Français", "English (US)", "Malagasy", "Español", "Deutsch", "Italiano", "Português", "Русский", "中文", "日本語", "한국어", "العربية", "हिन्दी", "Türkçe", "Nederlands", "Polski", "Svenska", "Tiếng Việt", "Ελληνικά", "Português (BR)"]
COMMANDO_LANGS = ["Français", "English (US)", "Malagasy"]

# --- 5. LOGIQUE D'AUTHENTIFICATION ---
if "auth_zip" not in st.session_state: 
    st.session_state.auth_zip = False

if not st.session_state.auth_zip:
    col_mid = st.columns([1, 1.5, 1])[1]
    with col_mid:
        st.markdown(display_logo_zip_css(), unsafe_allow_html=True)
        with st.container(border=True):
            u_mail = st.text_input("Identifiant zipngo").lower()
            u_pass = st.text_input("Mot de passe", type="password")
            u_role = st.selectbox("Grade Commando", list(COMMANDO_RULES.keys()))
            
            # Restriction Supermanager : Uniquement FR et US
            if u_role == "supermanager":
                login_langs = ["Français", "English (US)"]
            else:
                login_langs = COMMANDO_LANGS
                
            st.session_state.lang = st.selectbox("Langue d'interface", login_langs)
            
            if st.button("DÉVERROUILLER ZIPNGO"):
                st.session_state.update({"auth_zip": True, "user": u_mail, "role": u_role})
                st.rerun()
else:
    # --- 6. INTERFACE OPÉRATIONNELLE ---
    role = st.session_state.role
    
    with st.sidebar:
        st.markdown(display_logo_zip_css(), unsafe_allow_html=True)
        st.write(f"Grade : **{role.upper()}**")
        
        menu = st.radio("Navigation", [
            "📊 Dashboard zipngo", 
            "📞 Appels & Flux", 
            "⚡ Commando (Finances)", 
            "⚙️ Services Client",
            "🔒 Déconnexion"
        ])
        
        if menu == "🔒 Déconnexion":
            st.session_state.clear()
            st.rerun()

    # --- A. DASHBOARD ---
    if menu == "📊 Dashboard zipngo":
        st.header("📊 Pilotage de Flux")
        c1, c2, c3 = st.columns(3)
        c1.metric("CA Total", "125,400 €", "+5%")
        c2.metric("Taux de Conversion", "18%")
        c3.metric("Activité Équipe", "Optimale")

    # --- B. FLUX APPELS (SÉCURITÉ) ---
    elif menu == "📞 Appels & Flux":
        st.header("📞 Gestion des Flux")
        with st.container(border=True):
            col_n, col_t = st.columns([2, 2])
            col_n.write("👤 Prospect zipngo #44")
            
            if role == "supermanager":
                col_t.markdown("**+33 7 00 00 00 00** 📞")
            else:
                col_t.markdown("<span class='masked'>Numéro Masqué</span> 🔒", unsafe_allow_html=True)

    # --- C. MODE COMMANDO (VOS RÈGLES) ---
    elif menu == "⚡ Commando (Finances)":
        st.header("⚡ Calculateur Commando zipngo")
        montant = st.number_input("Montant Transaction (€)", min_value=0)
        config = COMMANDO_RULES[role]
        comm = montant * (config["fixe"] / 100)
        
        st.info(f"Grade : {config['label']}")
        st.success(f"Votre gain : {comm:.2f} €")
        
        if role == "manager":
            prime = 150000 * 0.10 # Simulation sur 150k de CA global
            st.write(f"Bonus Management (10% CA Global) : **{prime:.2f} €**")

    # --- D. SERVICES CLIENT ---
    elif menu == "⚙️ Services Client":
        st.header("⚙️ Configuration des Services")
        st.write("Le client gère ici ses propres départements.")
        
        target_lang = st.selectbox("Langue CRM Client (20 dispos)", ZIP_LANGS)
        
        with st.form("client_setup"):
            st.text_input("Nom du Service (ex: Logistique, Vente)")
            st.text_input("Chef de Service")
            st.slider("Commission Interne Client (%)", 0, 100, 15)
            st.form_submit_button("Valider les modifications")

st.markdown("<center style='font-size: 10px; color: gray; margin-top: 50px;'>© 2026 zipngo.zaxx | Powered by ZAXX Intelligence</center>", unsafe_allow_html=True)
