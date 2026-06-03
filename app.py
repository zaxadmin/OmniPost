import streamlit as st, pandas as pd, io, re, json
from supabase import create_client
from groq import Groq
from pypdf import PdfReader

# --- CONFIGURATION ---
st.set_page_config(page_title="zipngo | ATS Premium Global", layout="wide")
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- LISTE DES 20 LANGUES ---
LANGUES = [
    "Français", "English (US)", "Malagasy", "Español", "中文 (Mandarin)", 
    "العربية (Arabe)", "हिन्दी (Hindi)", "Bengali", "Português", "Русский", 
    "日本語 (Japonais)", "Deutsch", "한국어 (Coréen)", "Tiếng Việt", "Italiano", 
    "Türkçe", "Polski", "Nederlands", "Bahasa Indonesia", "ภาษาไทย (Thaï)"
]

def traduire_avec_ia(texte, langue_cible):
    if langue_cible == "Français": return texte
    # Note: En production, utilisez un dictionnaire JSON pour la performance
    prompt = f"Traduis le texte suivant en {langue_cible}. Renvoie uniquement le texte : {texte}"
    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
    return res.choices[0].message.content

# --- UI PRINCIPALE ---
st.markdown("<h1 style='color:#000080; margin-bottom: 0px;'>zip<span style='color:#4169E1;'>ngo</span>👍</h1>", unsafe_allow_html=True)

if 'langue' not in st.session_state: st.session_state.langue = "Français"
st.session_state.langue = st.selectbox("🌐 Sélectionner votre langue", LANGUES, index=0)

tab_home, tab_candidat, tab_employeur = st.tabs([traduire_avec_ia(n, st.session_state.langue) for n in ["🏠 Accueil", "🚀 Candidat", "💼 Employeur"]])

# --- ESPACE CANDIDAT ---
with tab_candidat:
    st.button("💎 " + traduire_avec_ia("Passer en Premium", st.session_state.langue), type="primary")
    # ... (Logique Candidat ici)

# --- ESPACE EMPLOYEUR ---
with tab_employeur:
    st.button("💎 " + traduire_avec_ia("Passer en Premium", st.session_state.langue), type="primary")
    # ... (Logique Employeur ici)

# --- ACCUEIL & CGV ---
with tab_home:
    with st.expander(traduire_avec_ia("⚖️ Conditions Générales de Vente & Utilisation", st.session_state.langue)):
        st.markdown(traduire_avec_ia("""
        ### Tarification :
        - **Accès Candidat :** 6€ pour 3 mois d'accès illimité.
        - **Accès Employeur :** 39€ par mois.
        
        ### Politique de Non-Remboursement :
        Les services étant numériques et à exécution immédiate, aucun remboursement ne sera effectué.
        
        ### Suppression de compte :
        Droit à l'effacement total de vos données sur simple demande par email à la créatrice. Traitement sous 48h.
        """, st.session_state.langue))

# --- PIED DE PAGE ---
st.markdown("---")
st.markdown(f"""
<div style='text-align: center;'>
    <p>Créatrice : <b>Liliane RAKOTOBE</b> 
    <a href="mailto:creationsites06@gmail.com" style="text-decoration: none; margin-left: 10px;">✉️</a></p>
</div>
""", unsafe_allow_html=True)
